"""E2E real de Chromium: importar, inferir demo, reabrir, PDF y móvil."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / 'evidencias_locales'
OUTPUT.mkdir(exist_ok=True)
HOST = 'http://127.0.0.1:8899'

with tempfile.TemporaryDirectory() as tmp:
    env = dict(os.environ, PYTHONPATH=str(BASE / 'src'), TRIA_STORAGE_DIR=tmp,
               TRIA_MODEL_BACKEND='demo')
    server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'tria.api:app',
                               '--host','127.0.0.1','--port','8899'],
                              cwd=BASE, env=env, stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE, text=True)
    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(HOST+'/health',timeout=.5) as reply:
                    if reply.status==200: break
            except Exception:
                time.sleep(.2)
        else: raise RuntimeError('El servidor no arrancó')
        subprocess.run([sys.executable, str(BASE/'scripts/generar_imagen_demo.py')],
                       cwd=BASE, check=True, capture_output=True)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':980},device_scale_factor=1,accept_downloads=True)
            errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.goto(HOST,wait_until='networkidle')
            assert 'PROYECTO ACADÉMICO' in page.locator('body').inner_text()
            assert page.locator('#empty').is_visible()
            page.screenshot(path=str(OUTPUT/'01_inicio.png'),full_page=True)
            page.locator('#image-file').set_input_files(str(BASE/'data/demo_geometrico.png'))
            page.locator('#upload-form button').click()
            page.get_by_text('Imagen aceptada y registrada.').wait_for(timeout=20000)
            assert page.locator('#study').is_visible()
            assert page.locator('#study-info').inner_text().count('SHA-256')==1
            page.screenshot(path=str(OUTPUT/'02_estudio.png'),full_page=True)
            page.locator('#analyse').click()
            page.get_by_text('Ejecución registrada.').wait_for(timeout=35000)
            assert page.locator('#analysis-status').inner_text()=='Prueba técnica'
            original_url=page.locator('#report-link').get_attribute('href')
            assert original_url.startswith('/api/v1/analyses/')
            assert page.locator('#scores').inner_text().find('Prueba técnica')>=0
            page.screenshot(path=str(OUTPUT/'03_resultados.png'),full_page=True)
            # Select a historical study after a fresh reload: do not regenerate inference.
            page.reload(wait_until='networkidle')
            assert page.locator('#results').is_hidden()
            page.locator('#history button').first.click()
            page.get_by_text('Estudio recuperado. Puedes consultar sus informes anteriores.').wait_for(timeout=20000)
            assert page.locator('#analysis-status').inner_text()=='Prueba técnica'
            assert page.locator('#report-link').get_attribute('href')==original_url
            with page.expect_download() as down:
                page.locator('#report-link').click()
            assert down.value.suggested_filename.lower().endswith('.pdf')
            page.screenshot(path=str(OUTPUT/'04_historial_recuperado.png'),full_page=True)
            # Same SPA is usable on a narrow viewport with no horizontal overflow.
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(OUTPUT/'05_movil.png'),full_page=True)
            overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth+2')
            assert not overflow, 'La interfaz desborda horizontalmente en móvil'
            assert not errors, 'Errores JS: '+repr(errors)
            browser.close()
        print(json.dumps({'ui_end_to_end':'OK','history_reload':'OK','pdf_download':'OK',
                          'mobile_overflow':False,'screenshots':[x.name for x in sorted(OUTPUT.glob('*.png'))]}))
    finally:
        server.terminate()
        try:server.communicate(timeout=6)
        except subprocess.TimeoutExpired:server.kill()
