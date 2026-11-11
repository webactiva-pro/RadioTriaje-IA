"""API local del prototipo TrIA NF3. PROHIBIDO USO ASISTENCIAL."""
from contextlib import asynccontextmanager
import hashlib
from io import BytesIO
from pathlib import Path
import json
import logging
import os
import re
import subprocess
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image

from tria import database as db
from tria.image_io import ImageRejected, validate_image
from tria.inference import create_backend, Result
from tria.provenance import source_for_sha256
from tria.report import make_pdf

LOG = logging.getLogger(__name__)
WEB = Path(__file__).parent / 'web'
ROOT = Path(__file__).resolve().parents[2]
DISCLAIMER = 'PROTOTIPO ACADÉMICO NO CLÍNICO. No usar con pacientes, diagnósticos ni triaje asistencial.'


def _revision() -> str | None:
    """HEAD con aviso +dirty; para ZIP sin git, usar TRIA_COMMIT_SHA explícita.

    El SHA Git identifica fuentes versionadas, no garantiza que el entorno
    Python o ficheros no versionados sean equivalentes.
    """
    supplied = os.environ.get('TRIA_COMMIT_SHA', '').strip().lower()
    if re.fullmatch('[0-9a-f]{40}', supplied):
        return supplied
    try:
        sha = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=ROOT,
                             capture_output=True, text=True, timeout=2, check=True).stdout.strip()
        if not re.fullmatch('[0-9a-f]{40}', sha):
            return None
        dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'],
                               cwd=ROOT, capture_output=True, text=True, timeout=3, check=True)
        return sha + ('+dirty' if dirty.stdout.strip() else '')
    except (OSError, subprocess.SubprocessError):
        return None


def create_app(storage_dir: Path | None = None, model_backend: str | None = None) -> FastAPI:
    root = Path(storage_dir or os.getenv('TRIA_STORAGE_DIR', '.tria-local')).resolve()
    mode = model_backend or os.getenv('TRIA_MODEL_BACKEND', 'demo')
    backend = create_backend(mode)
    software_revision = _revision()
    max_bytes = 12 * 1024 * 1024

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        (root / 'previews').mkdir(parents=True, exist_ok=True)
        (root / 'heatmaps').mkdir(parents=True, exist_ok=True)
        app.state.engine = db.open_database(root / 'tria.sqlite3')
        yield
        app.state.engine.dispose()

    app = FastAPI(title='TrIA NF3', version='0.2.0', lifespan=lifespan,
                  description=DISCLAIMER)
    app.mount('/assets', StaticFiles(directory=WEB), name='assets')

    def engine(request: Request):
        return request.app.state.engine

    def _with_map(record: dict) -> dict:
        return {**record, 'heatmap_available': (root / 'heatmaps' / (record['id'] + '.png')).is_file()}

    @app.get('/')
    def index():
        return FileResponse(WEB / 'index.html', media_type='text/html',
                            headers={'Cache-Control': 'no-store'})

    @app.get('/health')
    def health(request: Request):
        return {'status': 'ok', 'backend': mode, 'database': 'sqlite',
                'studies': db.counts(engine(request))['studies'], 'disclaimer': DISCLAIMER}

    @app.get('/api/v1/system')
    def system(request: Request):
        return {'mode': mode, 'model_version': backend.version,
                'model_loaded': mode == 'xrv' and getattr(backend, '_model', None) is not None,
                'real_medical_model_configured': mode == 'xrv',
                'real_medical_model_verified': mode == 'xrv' and getattr(backend, '_model', None) is not None,
                'software_revision': software_revision,
                'stats': db.counts(engine(request)), 'disclaimer': DISCLAIMER}

    @app.post('/api/v1/studies', status_code=201)
    async def upload_study(request: Request, file: UploadFile = File(...)):
        content = await file.read(max_bytes + 1)
        await file.close()
        try:
            processed = validate_image(content, max_bytes)
        except ImageRejected as exc:
            raise HTTPException(422, detail=str(exc)) from exc
        study_id = str(uuid.uuid4())
        path = root / 'previews' / (study_id + '.png')
        # No original pixels or filename are retained; normalized PNG and input hash only.
        path.write_bytes(processed.png)
        record = {
            'id': study_id, 'sha256': processed.sha256,
            'source_format': processed.source_format, 'width': processed.width,
            'height': processed.height, 'created_at': db.utc_now(),
            'warnings': json.dumps(processed.warnings, ensure_ascii=False),
            'provenance': json.dumps(source_for_sha256(processed.sha256), ensure_ascii=False),
        }
        try:
            db.insert_study(engine(request), record)
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return db.get_study(engine(request), study_id)

    @app.get('/api/v1/studies')
    def list_studies(request: Request):
        return db.list_studies(engine(request))

    @app.get('/api/v1/studies/{study_id}')
    def get_study(request: Request, study_id: str):
        record = db.get_study(engine(request), study_id)
        if not record:
            raise HTTPException(404, detail='Estudio no encontrado')
        return record

    @app.get('/api/v1/studies/{study_id}/preview')
    def preview(request: Request, study_id: str):
        if not db.get_study(engine(request), study_id):
            raise HTTPException(404, detail='Estudio no encontrado')
        path = root / 'previews' / (study_id + '.png')
        if not path.is_file():
            raise HTTPException(404, detail='Imagen normalizada no disponible')
        return FileResponse(path, media_type='image/png', headers={'Cache-Control': 'no-store'})

    @app.post('/api/v1/studies/{study_id}/analyses', status_code=201)
    def analyse(request: Request, study_id: str):
        study = db.get_study(engine(request), study_id)
        if not study:
            raise HTTPException(404, detail='Estudio no encontrado')
        try:
            with Image.open(root / 'previews' / (study_id + '.png')) as img:
                result = backend.infer(img)
        except Exception:
            LOG.exception('No se pudo ejecutar inferencia para estudio %s', study_id)
            result = Result(mode, backend.version, 'MODELO_NO_DISPONIBLE', {}, {},
                            'SIN_RESULTADO', 'Modelo no disponible; revisar pesos, dependencias y logs.')
        record = {
            'id': str(uuid.uuid4()), 'study_id': study_id, 'created_at': db.utc_now(),
            'mode': result.mode, 'model_version': result.model_version,
            'status': result.status, 'scores': json.dumps(result.scores),
            'features': json.dumps(result.features), 'indicator': result.indicator,
            'message': result.message,
            'weights_sha256': result.weights_sha256,
            'software_revision': software_revision,
            'gradcam_target': result.gradcam_target,
        }
        db.insert_analysis(engine(request), record)
        if result.heatmap_png:
            (root / 'heatmaps' / (record['id'] + '.png')).write_bytes(result.heatmap_png)
        return _with_map(db.get_analysis(engine(request), record['id']))

    @app.get('/api/v1/studies/{study_id}/analyses')
    def analyses_for_study(request: Request, study_id: str):
        if not db.get_study(engine(request), study_id):
            raise HTTPException(404, detail='Estudio no encontrado')
        return [_with_map(record) for record in db.list_analyses(engine(request), study_id)]

    @app.get('/api/v1/analyses/{analysis_id}')
    def analysis(request: Request, analysis_id: str):
        item = db.get_analysis(engine(request), analysis_id)
        if not item:
            raise HTTPException(404, detail='Análisis no encontrado')
        return _with_map(item)

    @app.get('/api/v1/analyses/{analysis_id}/heatmap')
    def heatmap(request: Request, analysis_id: str):
        if not db.get_analysis(engine(request), analysis_id):
            raise HTTPException(404, detail='Análisis no encontrado')
        path = root / 'heatmaps' / (analysis_id + '.png')
        if not path.is_file():
            raise HTTPException(404, detail='Mapa Grad-CAM no disponible')
        return FileResponse(path, media_type='image/png', headers={'Cache-Control': 'no-store'})

    @app.get('/api/v1/analyses/{analysis_id}/report')
    def report(request: Request, analysis_id: str):
        item = db.get_analysis(engine(request), analysis_id)
        if not item:
            raise HTTPException(404, detail='Análisis no encontrado')
        study = db.get_study(engine(request), item['study_id'])
        image_path = root / 'previews' / (study['id'] + '.png')
        heat_path = root / 'heatmaps' / (analysis_id + '.png')
        preview_png = image_path.read_bytes() if image_path.is_file() else None
        heatmap_png = heat_path.read_bytes() if heat_path.is_file() else None
        prov = study.get('provenance') or {}
        source_note = prov.get('label', 'Procedencia no acreditada')
        if prov.get('status') == 'coincidencia_sha256':
            source_note += ' · ' + prov.get('image_id', '') + ' · etiqueta NIH NLP: ' + prov.get('reference_label', '')
        document = make_pdf(study, item, preview_png=preview_png, heatmap_png=heatmap_png,
                            model_weights_sha256=item.get('weights_sha256'),
                            software_commit=item.get('software_revision'), source_note=source_note)
        return Response(document, media_type='application/pdf', headers={
            'Content-Disposition': 'attachment; filename="TrIA-informe-' + analysis_id[:8] + '.pdf"',
            'Cache-Control': 'no-store',
        })

    return app


# La entrada de Uvicorn activa IA salvo configuración explícita distinta.
# La factoría create_app conserva 'demo' para pruebas aisladas sin PyTorch.
app = create_app(model_backend=os.getenv('TRIA_MODEL_BACKEND', 'xrv'))
