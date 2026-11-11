"""Grad-CAM exploratorio. Un mapa de activación NO confirma lesiones."""
from io import BytesIO

import numpy as np
from PIL import Image


def heatmap_png(model, tensor, source: Image.Image, target_index: int) -> bytes:
    """Mapea gradientes de la última DenseBlock sobre una imagen de prueba.

    Específico de la arquitectura DenseNet-121 de TorchXRayVision.
    No implica validación clínica ni localización fiable de patologías.
    """
    import torch
    import torch.nn.functional as F

    captured = []
    layer = model.features.denseblock4
    handle = layer.register_forward_hook(lambda _module, _inputs, output: captured.append(output))
    try:
        with torch.enable_grad():
            output = model(tensor)
            if not captured:
                raise RuntimeError('No se capturaron activaciones de DenseNet')
            activations = captured[0]
            grad, = torch.autograd.grad(output[0, target_index], activations)
            weights = grad.mean(dim=(2, 3), keepdim=True)
            cam = F.relu((activations * weights).sum(dim=1, keepdim=True))
            cam = F.interpolate(cam, size=(source.height, source.width), mode='bilinear', align_corners=False)
            cam = cam[0, 0].detach().cpu().numpy()
    finally:
        handle.remove()

    if not np.isfinite(cam).all():
        raise RuntimeError('Grad-CAM tiene valores no finitos')
    low, high = float(cam.min()), float(cam.max())
    norm = (cam - low) / (high - low) if high > low else np.zeros_like(cam)
    # Máscara roja superpuesta en la imagen gris; solo representación heurística.
    mask = Image.fromarray(np.uint8(np.clip(norm * 165, 0, 165)), 'L')
    source_rgb = source.convert('RGB')
    overlay = Image.new('RGB', source_rgb.size, color=(235, 67, 43))
    result = Image.composite(overlay, source_rgb, mask)
    buf = BytesIO()
    result.save(buf, format='PNG')
    return buf.getvalue()
