"""Adaptadores: prueba de pipeline y modelo NIH externo inequívocamente separados."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import threading

import numpy as np
from PIL import Image

TARGETS = ('Pneumothorax', 'Effusion', 'Consolidation')


@dataclass(frozen=True)
class Result:
    mode: str
    model_version: str
    status: str
    scores: dict
    features: dict
    indicator: str
    message: str
    heatmap_png: bytes | None = None
    weights_sha256: str | None = None
    gradcam_target: str | None = None


class DemoBackend:
    """Estadísticas medibles: este modo NO infiere enfermedades."""
    mode = 'demo_sin_ia'
    version = 'image-stats-v1'

    def infer(self, image: Image.Image) -> Result:
        arr = np.asarray(image.convert('L'), dtype=np.float32)
        features = {
            'intensidad_media': round(float(arr.mean() / 255), 4),
            'contraste_desviacion': round(float(arr.std() / 255), 4),
            'fraccion_oscura': round(float((arr < 64).mean()), 4),
        }
        return Result(self.mode, self.version, 'DEMO_SIN_IA', {}, features,
                      'SIN_RESULTADO', 'Solo estadísticas de imagen. No hay clasificación radiológica activa.')


class XRayVisionBackend:
    """Inferencia no clínica con TorchXRayVision NIH DenseNet-121 y pesos externos."""
    mode = 'ml_preentrenado'
    version = 'torchxrayvision:densenet121-res224-nih'

    def __init__(self):
        self._model = None
        self._weights_digest = None
        # One model at a time: Grad-CAM attaches transient forward hooks.
        self._lock = threading.Lock()

    def _load(self, xrv):
        if self._model is not None:
            return
        model = xrv.models.DenseNet(weights='densenet121-res224-nih', apply_sigmoid=True)
        # Disable prepackaged operating thresholds: report raw sigmoid outputs.
        model.op_threshs = None
        model.eval()
        candidate = getattr(model, 'weights_filename_local', None)
        if candidate and Path(candidate).is_file():
            with Path(candidate).open('rb') as fh:
                self._weights_digest = hashlib.file_digest(fh, 'sha256').hexdigest()
        self._model = model

    def infer(self, image: Image.Image) -> Result:
        import torch
        import torchxrayvision as xrv
        from torchvision import transforms

        with self._lock:
            self._load(xrv)
            arr = np.asarray(image.convert('L'), dtype=np.float32)
            norm = xrv.datasets.normalize(arr, 255)[None, ...]
            transform = transforms.Compose([xrv.datasets.XRayCenterCrop(),
                                            xrv.datasets.XRayResizer(224)])
            tensor = torch.from_numpy(transform(norm)).float()[None, ...]
            with torch.inference_mode():
                values = self._model(tensor)[0].detach().cpu().numpy()
            scores = {key: round(float(values[list(self._model.pathologies).index(key)]), 5)
                      for key in TARGETS}
            target = max(TARGETS, key=lambda key: scores[key])
            try:
                from tria.gradcam import heatmap_png
                overlay = heatmap_png(self._model, tensor, image,
                                      list(self._model.pathologies).index(target))
                note = ' Mapa de activación disponible; no confirma ninguna lesión.'
                active_target = target
            except Exception:
                overlay = None
                active_target = None
                note = ' Grad-CAM no disponible en esta ejecución.'
            return Result(self.mode, self.version, 'EXPLORATORIO', scores, {}, 'SIN_RESULTADO',
                          'Puntuaciones no calibradas ni validadas clínicamente; sin prioridad asistencial.' + note,
                          heatmap_png=overlay, weights_sha256=self._weights_digest,
                          gradcam_target=active_target)


def create_backend(name: str):
    if name == 'demo':
        return DemoBackend()
    if name == 'xrv':
        return XRayVisionBackend()
    raise ValueError('TRIA_MODEL_BACKEND debe ser demo o xrv')
