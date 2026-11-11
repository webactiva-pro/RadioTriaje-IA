"""Smoke test con pesos REALES. No mide rendimiento ni aptitud clínica."""
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader
import hashlib
import json
import sys
import tempfile

from fastapi.testclient import TestClient

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tria.inference import XRayVisionBackend, TARGETS
from tria.api import create_app


def main():
    image_path = ROOT / 'data' / 'demo_geometrico.png'
    if not image_path.exists():
        raise SystemExit('Ejecutar antes: python scripts/generar_imagen_demo.py')
    backend = XRayVisionBackend()
    with Image.open(image_path) as image:
        result = backend.infer(image)
    assert result.status == 'EXPLORATORIO', result.status
    assert set(result.scores) == set(TARGETS), result.scores
    assert all(0 <= value <= 1 for value in result.scores.values()), result.scores
    assert result.heatmap_png is not None, 'Grad-CAM no se pudo generar'
    assert result.heatmap_png.startswith(b'\x89PNG')
    weights_file = Path(backend._model.weights_filename_local)
    assert weights_file.is_file(), 'Faltan pesos preentrenados'
    digest = hashlib.sha256(weights_file.read_bytes()).hexdigest()
    # Verificación de INTEGRACIÓN real: web API, persistencia, modelo,
    # visualización de activaciones y PDF, todo con una imagen sintética.
    with tempfile.TemporaryDirectory() as work:
        with TestClient(create_app(Path(work), model_backend='xrv')) as api:
            up = api.post('/api/v1/studies', files={'file': ('demo.png', image_path.read_bytes(), 'image/png')})
            assert up.status_code == 201, up.text
            study_id = up.json()['id']
            analysed = api.post('/api/v1/studies/' + study_id + '/analyses')
            assert analysed.status_code == 201, analysed.text
            item = analysed.json()
            assert item['status'] == 'EXPLORATORIO', item
            assert item['mode'] == 'ml_preentrenado', item
            assert set(item['scores']) == set(TARGETS), item
            assert item['indicator'] == 'SIN_RESULTADO', item
            assert item['heatmap_available'] is True, item
            assert api.get('/api/v1/analyses/' + item['id'] + '/heatmap').content.startswith(b'\x89PNG')
            pdf=api.get('/api/v1/analyses/' + item['id'] + '/report').content
            parsed=PdfReader(BytesIO(pdf))
            assert len(parsed.pages)==2
            assert len(parsed.pages[0].images)>=2, 'Radiografía y Grad-CAM faltantes'
            detail=parsed.pages[1].extract_text()
            assert up.json()['sha256'] in detail, 'Falta SHA de archivo original'
            assert digest in detail, 'Falta SHA de pesos del modelo'
            assert item['weights_sha256']==digest, 'No se persistió la huella del checkpoint'
            evidence=ROOT/'evidencias_locales';evidence.mkdir(exist_ok=True)
            (evidence/'TrIA_informe_IA_sintetica.pdf').write_bytes(pdf)
            assert api.get('/api/v1/system').json()['stats'] == {'studies': 1, 'analyses': 1}
    output = {'verificacion': 'ok', 'api_integracion': 'ok', 'archivo_ejemplo': 'sintetico (no radiografia)',
              'modelo': result.model_version, 'sha256_pesos': digest,
              'scores_solo_smoke_test': result.scores,
              'gradcam_png': bool(result.heatmap_png), 'no_clinico': True}
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
