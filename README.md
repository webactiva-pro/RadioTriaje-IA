# TrIA · Análisis de radiografías torácicas

TrIA es una aplicación web local que permite importar radiografías de tórax, ejecutar un modelo de clasificación preentrenado y consultar sus resultados. Incluye visualización Grad-CAM, historial de estudios e informes PDF con los datos de cada ejecución.

**Trabajo académico — Grupo 8 · Proyecto de Inteligencia Artificial y Big Data (NF3).** El modelo se utiliza con fines experimentales: sus puntuaciones no están validadas para diagnóstico ni para establecer prioridades médicas.

## Ejecutar en Windows

Se requiere **Git, Python 3.11 o 3.13 y conexión a Internet**. Copia este bloque completo en una consola **CMD** nueva:

```cmd
cd /d "%USERPROFILE%"
git clone https://github.com/webactiva-pro/RadioTriaje-IA.git RadioTriaje-NF3-evaluacion
cd RadioTriaje-NF3-evaluacion
iniciar_tria_windows.cmd
```

El lanzador crea el entorno de Python, instala las dependencias y abre **http://127.0.0.1:8000**. La primera inferencia puede necesitar descargar los pesos de DenseNet-121.

Para empezar con **radiografías reales del conjunto público NIH**, abre la [muestra de 20 casos](examples/nih/README.md) y selecciona uno de los PNG que están en `examples/nih/radiografias/`. El resultado se obtiene con **Cargar imagen → Ejecutar análisis**. El historial permite reabrir análisis y descargar el informe PDF.

Si el repositorio ya está clonado, usa `git pull --ff-only` desde su carpeta y ejecuta `iniciar_tria_windows.cmd`. El modo `iniciar_tria_windows.cmd demo` existe solo para pruebas del software sin cargar el modelo.

## Radiografías y resultados

[**Ver las 20 radiografías NIH, etiquetas originales, puntuaciones y hashes**](examples/nih/README.md)

El conjunto de ejemplos incluye una imagen por fichero, la etiqueta NIH disponible, tres puntuaciones generadas por el modelo, el SHA-256 del archivo original y el registro de procedencia. Las etiquetas proceden de informes procesados automáticamente; no constituyen diagnósticos verificados por el grupo.

## Organización del proyecto

| Carpeta | Contenido |
|---|---|
| [`src/tria/`](src/tria/) | API, carga y preprocesamiento, inferencia, Grad-CAM, SQLite e informes |
| [`src/tria/web/`](src/tria/web/) | Interfaz HTML, CSS y JavaScript |
| [`examples/nih/`](examples/nih/) | 20 radiografías NIH con sus resultados y datos de procedencia |
| [`tests/`](tests/) | Pruebas unitarias e integración |
| [`scripts/`](scripts/) | Generación de imágenes de prueba, lote NIH y pruebas técnicas |
| [`environment/`](environment/) | Dependencias base, de desarrollo y del modelo |
| [`.github/workflows/`](.github/workflows/) | Ejecuciones automáticas del backend, navegador e IA |
| [`docs/`](docs/) | Historia del proyecto, diseño, arquitectura, decisiones y evaluación |

> La carpeta `data/` se utiliza para archivos generados localmente y no contiene radiografías versionadas. Las imágenes publicadas están en `examples/nih/radiografias/`.

## Documentación

[**Índice de documentación**](docs/README.md) · [Evolución desde Fase 0 y NF2](docs/01_CONTEXTO_Y_FASES.md) · [Arquitectura y requisitos](docs/02_DISENO_Y_ARQUITECTURA.md) · [Decisiones de implementación](docs/03_IMPLEMENTACION_Y_DECISIONES.md) · [Datos y evaluación](docs/04_DATOS_Y_RESULTADOS.md) · [Reproducibilidad](docs/05_EJECUCION_Y_VERIFICACION.md)

El código y las pruebas pueden consultarse sin instalar nada en [GitHub Actions](https://github.com/webactiva-pro/RadioTriaje-IA/actions). Esta es una copia de entrega pública; el desarrollo anterior se realizó en un repositorio privado. No se ha importado su historial ni documentación grupal con datos personales.

## Créditos y límites

El modelo y los pesos proceden de [TorchXRayVision](https://github.com/mlmed/torchxrayvision) (Joseph P. Cohen y colaboradores). Las imágenes son del conjunto [NIH ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC), publicado por el **NIH Clinical Center**, y deben citarse con Wang et al., *ChestX-ray8* (CVPR 2017, DOI [10.1109/CVPR.2017.369](https://doi.org/10.1109/CVPR.2017.369)). La publicación de esta selección se basa en los términos NIH de uso abierto con atribución; las imágenes se obtuvieron de un espejo público y se identifican con hashes, sin confirmar coincidencia binaria con los originales del NIH.

Se ha usado ChatGPT como apoyo en estructura, programación, pruebas y documentación. TrIA no incluye entrenamiento propio acreditado, evaluación clínica independiente ni un motor de triaje asistencial.
