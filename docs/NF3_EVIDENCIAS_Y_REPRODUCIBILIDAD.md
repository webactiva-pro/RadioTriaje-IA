# Evidencias reproducibles de NF3

Este documento describe los controles del repositorio **público**. Las ejecuciones anteriores del fork privado no se presentan como evidencia pública; se han configurado workflows para repetir los ensayos aquí.

## Comprobaciones automatizadas

| Workflow | Qué comprueba | Cómo se reproduce |
|---|---|---|
| [Pruebas de reproducibilidad](../.github/workflows/nf3-tests.yml) | Instalación desde cero y pytest en Python 3.11/3.13 | Se ejecuta al publicar `main` y en PR |
| [Navegador E2E](../.github/workflows/nf3-e2e.yml) | Flujo de subida, análisis técnico, recarga, historial, PDF y móvil | Se ejecuta al publicar `main` |
| [IA y PDF](../.github/workflows/nf3-ml-smoke.yml) | Pesos reales TorchXRayVision, inferencia, Grad-CAM, SQLite e informe PDF | Se ejecuta al publicar `main` |
| [Lote NIH](../.github/workflows/nf3-nih-sanity.yml) | Descarga y evaluación exploratoria de 20 radiografías con etiquetas NIH | Ejecución manual desde Actions (requiere red y pesos) |

Los enlaces a ejecuciones concretas deben obtenerse de [Actions](https://github.com/webactiva-pro/RadioTriaje-IA/actions). **No declarar un resultado aprobado hasta comprobar que su ejecución terminó en `success`.**

## Datos NIH conservados en Git

Los ficheros [manifiesto](NF3_NIH_20_MANIFEST.json), [resultados](NF3_NIH_20_RESULTADOS.csv) y [resumen](NF3_NIH_20_RESUMEN.json) documentan la muestra de 20 radiografías con imágenes y etiquetas obtenidas de una copia pública del dataset NIH. Se conservan IDs técnicos, URL de origen y SHA-256, pero no se redistribuyen PNG en el código. El análisis se realizó previamente con el mismo modelo, sin reclamar independencia clínica o generalización.

**Limitaciones:** etiquetas NIH extraídas de informes con NLP, selección de muestra deliberada y pequeña, checkpoint entrenado en dominio NIH, ausencia de calibración y de análisis clínico externo. No utilizar porcentajes como probabilidades diagnósticas ni Grad-CAM como confirmación de lesión.

## Procedimiento manual

1. Leer el [README](../README.md) y abrir el repositorio en el commit que se indique en Blackboard.
2. En Windows, ejecutar `iniciar_tria_windows.cmd` desde una instalación nueva con Python 3.11/3.13.
3. Cargar el patrón artificial generado por el script, ejecutar el análisis y descargar el PDF.
4. Reabrir el estudio histórico y verificar que no se vuelve a ejecutar el modelo y que el SHA original se conserva.
5. Para validar el motor en GitHub, consultar el smoke XRV y comprobar los hashes incluidos en el artefacto del workflow.

**Atribución:** TorchXRayVision, Cohen y colaboradores; NIH ChestX-ray14, Wang y colaboradores (CVPR 2017). El desarrollo fue asistido por ChatGPT, declarado en README y memoria académica.
