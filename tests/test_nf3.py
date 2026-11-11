"""Pruebas ejecutables: el proyecto no se evalúa por capturas de código."""
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tria.api import create_app
from tria.image_io import validate_image, ImageRejected
from tria.inference import DemoBackend


def fake_png(width=256, height=256):
    buff = BytesIO()
    Image.new('L', (width, height), color=127).save(buff, format='PNG')
    return buff.getvalue()


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path)) as api:
        yield api


def test_root_and_health(client):
    assert client.get('/').status_code == 200
    assert 'PROYECTO ACADÉMICO' in client.get('/').text
    assert client.get('/health').json()['status'] == 'ok'
    assert client.get('/api/v1/system').json()['real_medical_model_configured'] is False


def test_complete_flow_and_pdf(client):
    uploaded = client.post('/api/v1/studies', files={'file': ('demo.png', fake_png(), 'image/png')})
    assert uploaded.status_code == 201, uploaded.text
    study = uploaded.json()
    assert len(study['sha256']) == 64
    assert study['width'] == 256
    assert client.get('/api/v1/studies/' + study['id']).json()['id'] == study['id']
    preview = client.get('/api/v1/studies/' + study['id'] + '/preview')
    assert preview.status_code == 200 and preview.content.startswith(b'\x89PNG')
    analysis_resp = client.post('/api/v1/studies/' + study['id'] + '/analyses')
    assert analysis_resp.status_code == 201, analysis_resp.text
    analysis = analysis_resp.json()
    assert analysis['status'] == 'DEMO_SIN_IA'
    assert analysis['indicator'] == 'SIN_RESULTADO'
    assert analysis['scores'] == {}
    assert 'intensidad_media' in analysis['features']
    assert client.get('/api/v1/analyses/' + analysis['id']).status_code == 200
    assert len(client.get('/api/v1/studies/' + study['id'] + '/analyses').json()) == 1
    report = client.get('/api/v1/analyses/' + analysis['id'] + '/report')
    assert report.status_code == 200 and report.content.startswith(b'%PDF-')
    assert client.get('/api/v1/system').json()['stats'] == {'studies': 1, 'analyses': 1}


def test_reject_bad_files(client):
    for payload in (b'', b'no es imagen', b'A' * (12 * 1024 * 1024 + 1)):
        response = client.post('/api/v1/studies', files={'file': ('bad.png', payload, 'image/png')})
        assert response.status_code == 422
    assert client.get('/api/v1/studies').json() == []


def test_reject_too_small(client):
    response = client.post('/api/v1/studies', files={'file': ('small.png', fake_png(16, 16), 'image/png')})
    assert response.status_code == 422


def test_reject_gif(client):
    buff = BytesIO()
    Image.new('L', (100, 100), color=0).save(buff, format='GIF')
    response = client.post('/api/v1/studies', files={'file': ('bad.gif', buff.getvalue(), 'image/gif')})
    assert response.status_code == 422


def test_nonexistent_ids(client):
    identifier = '00000000-0000-0000-0000-000000000000'
    assert client.get('/api/v1/studies/' + identifier).status_code == 404
    assert client.get('/api/v1/studies/' + identifier + '/preview').status_code == 404
    assert client.post('/api/v1/studies/' + identifier + '/analyses').status_code == 404
    assert client.get('/api/v1/analyses/' + identifier + '/report').status_code == 404


def test_database_persists_across_restart(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        study = client.post('/api/v1/studies', files={'file': ('test.png', fake_png(), 'image/png')}).json()
    with TestClient(create_app(tmp_path)) as client:
        assert client.get('/api/v1/studies/' + study['id']).status_code == 200
        assert client.get('/api/v1/system').json()['stats']['studies'] == 1


def test_original_filename_not_persisted(client, tmp_path):
    client.post('/api/v1/studies', files={'file': ('NOMBRE_PACIENTE_123.png', fake_png(), 'image/png')})
    names = [p.name for p in tmp_path.rglob('*') if p.is_file()]
    assert not any('NOMBRE_PACIENTE' in name for name in names)


def test_demo_scores_not_masquerading_as_disease():
    with Image.open(BytesIO(fake_png())) as image:
        result = DemoBackend().infer(image)
    assert result.scores == {}
    assert result.indicator == 'SIN_RESULTADO'
    assert result.model_version == 'image-stats-v1'


def test_xrv_unavailable_never_fabricates_scores(monkeypatch, tmp_path):
    from tria.inference import XRayVisionBackend
    def missing(_image):
        raise RuntimeError('sin pesos')
    monkeypatch.setattr(XRayVisionBackend, 'infer', missing)
    with TestClient(create_app(tmp_path, model_backend='xrv')) as client:
        study = client.post('/api/v1/studies', files={'file': ('demo.png', fake_png(), 'image/png')}).json()
        response = client.post('/api/v1/studies/' + study['id'] + '/analyses')
        assert response.status_code == 201
        result = response.json()
        assert result['status'] == 'MODELO_NO_DISPONIBLE'
        assert result['scores'] == {} and result['indicator'] == 'SIN_RESULTADO'


def test_dicom_with_identifying_metadata_is_rejected():
    pydicom = pytest.importorskip('pydicom')
    from pydicom.dataset import FileDataset, FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid
    meta = FileMetaDataset()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    dicom = FileDataset('test.dcm', {}, file_meta=meta, preamble=b'\0' * 128)
    dicom.Modality = 'DX'
    dicom.PatientName = 'PERSONA DE PRUEBA'
    data = BytesIO()
    dicom.save_as(data, enforce_file_format=True)
    with pytest.raises(ImageRejected, match='metadatos identificativos'):
        validate_image(data.getvalue(), 12 * 1024 * 1024)


def test_synthetic_dicom_monochrome_is_processed():
    pydicom = pytest.importorskip('pydicom')
    import numpy as np
    from pydicom.dataset import FileDataset, FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid
    meta = FileMetaDataset()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    dicom = FileDataset('test.dcm', {}, file_meta=meta, preamble=b'\0' * 128)
    dicom.Modality = 'DX'
    dicom.Rows = 64; dicom.Columns = 64
    dicom.PhotometricInterpretation = 'MONOCHROME2'; dicom.SamplesPerPixel = 1
    dicom.BitsAllocated = 8; dicom.BitsStored = 8; dicom.HighBit = 7; dicom.PixelRepresentation = 0
    dicom.PixelData = np.arange(64*64, dtype=np.uint8).reshape(64,64).tobytes()
    data = BytesIO(); dicom.save_as(data, enforce_file_format=True)
    image = validate_image(data.getvalue(), 12 * 1024 * 1024)
    assert image.source_format == 'DICOM' and image.width == 64


def test_gradcam_on_lightweight_torch_fixture():
    torch = pytest.importorskip('torch')
    from torch import nn
    from tria.gradcam import heatmap_png

    class ToyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Module()
            self.features.denseblock4 = nn.Conv2d(1, 4, kernel_size=3, padding=1)
            self.head = nn.Linear(4, 3)
        def forward(self, x):
            z = torch.relu(self.features.denseblock4(x))
            return self.head(z.mean(dim=(2, 3)))

    image = Image.new('L', (32, 32), color=128)
    tensor = torch.ones(1, 1, 32, 32)
    out = heatmap_png(ToyNet(), tensor, image, 1)
    assert out.startswith(b'\x89PNG')


def test_demo_heatmap_endpoint_returns_404(client):
    study = client.post('/api/v1/studies', files={'file': ('demo.png', fake_png(), 'image/png')}).json()
    analysis = client.post('/api/v1/studies/' + study['id'] + '/analyses').json()
    assert analysis['heatmap_available'] is False
    assert client.get('/api/v1/analyses/' + analysis['id'] + '/heatmap').status_code == 404


def test_pdf_visual_two_pages_with_original_hash(client):
    from pypdf import PdfReader
    image=fake_png(256,256)
    upload=client.post('/api/v1/studies',files={'file':('test.png',image,'image/png')})
    assert upload.status_code == 201
    study=upload.json()
    analysis=client.post('/api/v1/studies/'+study['id']+'/analyses').json()
    response=client.get('/api/v1/analyses/'+analysis['id']+'/report')
    document=PdfReader(BytesIO(response.content))
    assert len(document.pages)==2
    assert len(document.pages[0].images)>=1
    assert study['sha256'] in document.pages[1].extract_text()
    assert analysis['id'] in document.pages[1].extract_text()
    assert 'No apto para diagnóstico' in document.pages[0].extract_text()
    assert 'No registrado para esta ejecución' in document.pages[1].extract_text()


def test_historical_hashes_are_not_regenerated_from_current_model(monkeypatch, tmp_path):
    from tria.inference import XRayVisionBackend, Result
    from pypdf import PdfReader
    saved='a'*64
    def historical_test(_self,_image):
        return Result('ml_preentrenado','modelo-prueba', 'EXPLORATORIO',
                      {'Effusion':0.21}, {}, 'SIN_RESULTADO','Prueba de persistencia',
                      weights_sha256=saved, gradcam_target=None)
    monkeypatch.setattr(XRayVisionBackend,'infer',historical_test)
    with TestClient(create_app(tmp_path,model_backend='xrv')) as api:
        study=api.post('/api/v1/studies',files={'file':('test.png',fake_png(),'image/png')}).json()
        analysis=api.post('/api/v1/studies/'+study['id']+'/analyses').json()
        assert analysis['weights_sha256']==saved
        assert analysis['gradcam_target'] is None
    # Another process/same storage with DEMO backend should not erase/replace provenance.
    with TestClient(create_app(tmp_path,model_backend='demo')) as api:
        stored=api.get('/api/v1/analyses/'+analysis['id']).json()
        assert stored['weights_sha256']==saved
        report=api.get('/api/v1/analyses/'+analysis['id']+'/report')
        text=PdfReader(BytesIO(report.content)).pages[1].extract_text()
        assert saved in text
        assert 'modelo-prueba' in text
        assert stored['mode']=='ml_preentrenado'


def test_existing_database_is_migrated_without_deleting_studies(tmp_path):
    import sqlite3
    db_path=tmp_path/'tria.sqlite3'
    with sqlite3.connect(db_path) as connection:
        connection.execute('CREATE TABLE studies (id VARCHAR PRIMARY KEY, sha256 VARCHAR(64), source_format VARCHAR(10), width INTEGER, height INTEGER, created_at VARCHAR(40), warnings TEXT)')
        connection.execute('CREATE TABLE analyses (id VARCHAR PRIMARY KEY, study_id VARCHAR, created_at VARCHAR(40), mode VARCHAR, model_version VARCHAR, status VARCHAR, scores TEXT, features TEXT, indicator VARCHAR, message TEXT)')
        connection.execute('INSERT INTO studies VALUES (?,?,?,?,?,?,?)',('historico','b'*64,'PNG',256,256,'2026-10-10T12:00:00Z','[]'))
        connection.execute('INSERT INTO analyses VALUES (?,?,?,?,?,?,?,?,?,?)',('analisis-viejo','historico','2026-10-10T12:00:01Z','demo_sin_ia','old','DEMO_SIN_IA','{}','{}','SIN_RESULTADO','Anterior'))
    with TestClient(create_app(tmp_path)) as api:
        legacy=api.get('/api/v1/studies/historico')
        assert legacy.status_code==200
        assert legacy.json()['provenance']['status']=='sin_acreditar'
        legacy_analysis=api.get('/api/v1/analyses/analisis-viejo')
        assert legacy_analysis.status_code==200
        assert legacy_analysis.json()['weights_sha256'] is None
        new_study=api.post('/api/v1/studies',files={'file':('test.png',fake_png(),'image/png')})
        assert new_study.status_code==201
        assert api.get('/api/v1/system').json()['stats']['studies']==2


def test_study_history_can_be_reopened_with_analyses(client):
    study=client.post('/api/v1/studies',files={'file':('demo.png',fake_png(),'image/png')}).json()
    result1=client.post('/api/v1/studies/'+study['id']+'/analyses').json()
    result2=client.post('/api/v1/studies/'+study['id']+'/analyses').json()
    result=client.get('/api/v1/studies/'+study['id']+'/analyses')
    assert result.status_code==200
    ids={r['id'] for r in result.json()}
    assert ids == {result1['id'],result2['id']}
    for record in result.json():
        assert record['heatmap_available'] is False
        assert client.get('/api/v1/analyses/'+record['id']).status_code==200
        assert client.get('/api/v1/analyses/'+record['id']+'/report').status_code==200


def test_source_provenance_is_hash_matched_only(tmp_path):
    import hashlib, json
    from tria.provenance import source_for_sha256
    known='b'*64
    manifest=tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'samples':[{'sha256':known,'image_id':'test.png',
        'group':'Effusion','view':'PA'}]}),encoding='utf8')
    assert source_for_sha256(known,manifest)['status']=='coincidencia_sha256'
    assert source_for_sha256('c'*64,manifest)['status']=='sin_acreditar'
    assert source_for_sha256('fake-sha',manifest)['status']=='sin_acreditar'


def test_pdf_includes_two_different_images_when_supplied():
    from tria.report import make_pdf
    from pypdf import PdfReader
    study={'id':'s','sha256':'a'*64,'source_format':'PNG','width':256,'height':256}
    analysis={'id':'a','created_at':'2026-11-10T00:00:00Z','mode':'ml_preentrenado',
              'model_version':'test','status':'EXPLORATORIO','scores':{'Effusion':0.2},
              'features':{},'message':'Solo ensayo no clínico','indicator':'SIN_RESULTADO',
              'gradcam_target':'Effusion'}
    pdf=make_pdf(study,analysis,preview_png=fake_png(256,256),heatmap_png=fake_png(255,256),
                 model_weights_sha256='b'*64,software_commit='c'*40)
    document=PdfReader(BytesIO(pdf))
    assert len(document.pages)==2
    assert len(document.pages[0].images)>=2
    assert 'a'*64 in document.pages[1].extract_text()
    assert 'b'*64 in document.pages[1].extract_text()
    assert 'c'*40 in document.pages[1].extract_text()


def test_default_uvicorn_backend_is_ai_unless_explicitly_overridden():
    import os
    from tria.api import app
    if os.environ.get('TRIA_MODEL_BACKEND'):
        pytest.skip('Backend fijado por el entorno')
    with TestClient(app) as client:
        assert client.get('/api/v1/system').json()['mode'] == 'xrv'


def test_windows_launcher_uses_compatible_isolated_environment_and_valid_ml_path():
    code = (Path(__file__).resolve().parents[1] / 'iniciar_tria_windows.cmd').read_text(encoding='utf-8')
    assert r'environment\requirements-ml.txt' in code
    assert r'.venv-tria\Scripts\python.exe' in code
    assert 'set "TRIA_MODEL_BACKEND=xrv"' in code
    assert 'if /I "%~1"=="demo"' in code


def test_readme_contains_copyable_windows_cmd_start():
    readme = (Path(__file__).resolve().parents[1] / 'README.md').read_text(encoding='utf-8')
    section = readme.split('## Ejecutar TrIA en Windows', 1)[1].split('## Qué se entrega', 1)[0]
    block = section.split('```cmd', 1)[1].split('```', 1)[0]
    commands = [line.strip() for line in block.splitlines() if line.strip()]
    assert commands == [
        'cd /d "%USERPROFILE%"',
        'git clone https://github.com/webactiva-pro/RadioTriaje-IA.git RadioTriaje-NF3-evaluacion',
        'cd RadioTriaje-NF3-evaluacion',
        'iniciar_tria_windows.cmd',
    ]
