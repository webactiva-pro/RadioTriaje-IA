"""Proveniencia por coincidencia binaria de SHA-256, nunca por nombre de fichero.

Solo se reconoce una imagen NIH si coincide *exactamente* con un SHA registrado
para la muestra académica. Ni siquiera ese match demuestra que las etiquetas
sean una verdad clínica validada o que el espejo sea idéntico al NIH original.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / 'docs' / 'NF3_NIH_20_MANIFEST.json'
SHA64 = re.compile(r'^[a-f0-9]{64}$')


def source_for_sha256(sha256: str, manifest_path: Path | None = None) -> dict:
    default = {'status': 'sin_acreditar', 'label': 'Procedencia no acreditada'}
    if not SHA64.fullmatch(sha256 or ''):
        return default
    filename = manifest_path or DEFAULT_MANIFEST
    try:
        if filename.stat().st_size > 512_000:
            return default
        data = json.loads(filename.read_text(encoding='utf-8'))
        for row in data.get('samples', []):
            if row.get('sha256') == sha256:
                return {
                    'status': 'coincidencia_sha256',
                    'label': 'NIH ChestX-ray14 · muestra académica etiquetada',
                    'image_id': row['image_id'],
                    'reference_label': row['group'],
                    'view': row.get('view', 'No indicada'),
                    'source': 'NIH Clinical Center, Wang et al. CVPR 2017',
                    'qualification': ('Coincidencia de bytes con copia pública; etiquetas NIH NLP; '
                                      'espejo no contrastado binariamente con el original.'),
                }
    except (OSError, ValueError, TypeError, KeyError):
        return default
    return default
