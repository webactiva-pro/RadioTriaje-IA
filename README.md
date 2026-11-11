# TrIA — RadioTriaje-AI · Grupo 8 · NF3

Aplicación académica local de análisis exploratorio de radiografías torácicas mediante un modelo preentrenado DenseNet-121. Incluye carga y control de imágenes, puntuaciones, mapa Grad-CAM, historial en SQLite e informes PDF trazables.

**Para el profesor:** [guía de evaluación rápida](docs/GUIA_EVALUADOR_NF3.md). El repositorio es público; se puede consultar el código y las pruebas de GitHub Actions sin solicitar acceso. La memoria académica completa se entrega como PDF en Blackboard.

## Ejecutar TrIA en Windows — copiar y pegar en CMD

**Requisitos:** Git, Python 3.11 o 3.13 y conexión a Internet. Usar una ventana nueva de **CMD de Windows**. El directorio `RadioTriaje-NF3-evaluacion` no debe existir previamente.

```cmd
cd /d "%USERPROFILE%"
git clone https://github.com/webactiva-pro/RadioTriaje-IA.git RadioTriaje-NF3-evaluacion
cd RadioTriaje-NF3-evaluacion
iniciar_tria_windows.cmd
```

El lanzador prepara un entorno independiente `.venv-tria`, instala las dependencias de IA y abre `http://127.0.0.1:8000`. En el primer análisis descarga los pesos preentrenados. El motor normal es **IA NIH**. No hace falta ejecutar instrucciones de Linux ni activar Python manualmente.

El flujo es **seleccionar → cargar → analizar → ver Grad-CAM → descargar PDF → reabrir desde historial**. Para probar sin radiografías, cargar `data/demo_geometrico.png` (imagen artificial generada por el lanzador). La inferencia sobre esa imagen solo comprueba funcionamiento técnico.

**Solo para pruebas sin IA:** `iniciar_tria_windows.cmd demo`. Este modo calcula estadísticas de imagen y no representa el uso habitual de la aplicación.

## Qué se entrega

- **Frontend:** HTML/CSS/JS adaptable, validación visible, lectura de resultados y recuperación de estudios.
- **Backend:** FastAPI y SQLite/SQLAlchemy; API REST para estudios, análisis, imágenes, informes y auditoría.
- **Modelo experimental:** TorchXRayVision DenseNet-121 NIH con pesos externos, tres puntuaciones no calibradas: neumotórax, derrame pleural y consolidación.
- **Explicabilidad:** superposición Grad-CAM de activaciones, sin afirmaciones de localización anatómica validada.
- **Evidencias:** informes PDF con imagen, mapa disponible, fecha, origen, identificadores, SHA-256 y revisión cuando se conoce.
- **Pruebas:** suite pytest, navegador Chromium, smoke IA con pesos reales, muestra exploratoria etiquetada NIH de 20 imágenes.

## Verificar el producto sin instalarlo

En [GitHub Actions](https://github.com/webactiva-pro/RadioTriaje-IA/actions) pueden consultarse los workflows de **pruebas Python 3.11/3.13**, **navegador** e **inferencia con pesos reales**. El workflow NIH adicional es de ejecución manual. Los archivos de código, pruebas y resultados tabulares NIH están versionados en este repositorio, sin distribuir datos de pacientes ni pesos de terceros.

Documentación: [guía del evaluador](docs/GUIA_EVALUADOR_NF3.md) · [arquitectura y correspondencia NF2→NF3](docs/NF3_ESTADO_IMPLEMENTACION.md) · [protocolo NIH](docs/NF3_VALIDACION_NIH.md) · [manifiesto y hashes](docs/NF3_NIH_20_MANIFEST.json) · [resultados](docs/NF3_NIH_20_RESULTADOS.csv).

## Instalación manual en Linux/macOS

Solo si no se usa Windows; estos comandos **no son para CMD**.

```bash
git clone https://github.com/webactiva-pro/RadioTriaje-IA.git
cd RadioTriaje-IA
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r environment/requirements-ml.txt
python -m pip install -e . --no-deps
python -m uvicorn tria.api:app --host 127.0.0.1 --port 8000
```

Para ejecutar la suite sin PyTorch: `python -m pip install -r environment/requirements-dev.txt`, después `python -m pip install -e . --no-deps` y `python -m pytest -q tests`. La aplicación inicia el motor de IA por defecto; el modo sin IA se utiliza únicamente en pruebas.

## Alcance, procedencia y atribuciones

Esta es una **demostración informática académica**, no una herramienta para diagnóstico o priorización médica. Las puntuaciones no están calibradas ni validadas clínicamente, Grad-CAM no verifica lesiones, y el conjunto NIH no constituye una validación independiente del modelo entrenado en ese dominio. No subir ni procesar información identificable de pacientes.

Modelo y librería externos: [TorchXRayVision](https://github.com/mlmed/torchxrayvision), Joseph P. Cohen y colaboradores ([publicación](https://arxiv.org/abs/2111.00595)). Dataset: [NIH ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC), Wang et al. (CVPR 2017), DOI [10.1109/CVPR.2017.369](https://doi.org/10.1109/CVPR.2017.369). Se empleó ChatGPT como asistencia en implementación, pruebas, interfaz y documentación; los resultados se reportan con evidencias de ejecución.

**Publicación para evaluación:** esta copia contiene exclusivamente los archivos técnicos de NF3 y documentos públicos seleccionados, sin el historial del fork privado. No incluye pesos, radiografías originales ni documentos académicos previos con datos de los integrantes. No se concede una licencia general de reutilización sobre las contribuciones del grupo.
