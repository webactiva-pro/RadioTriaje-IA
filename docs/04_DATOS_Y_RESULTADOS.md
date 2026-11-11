# 04 · Datos, muestra NIH y resultados

## Procedencia

Se utilizaron imágenes del conjunto **NIH ChestX-ray14**, proporcionado por el NIH Clinical Center, que contiene radiografías torácicas etiquetadas a partir de informes mediante NLP. La muestra elegida comprende 20 PNG procedentes del conjunto de test indicado en los metadatos NIH: cinco con etiqueta única para cada hallazgo elegido y cinco marcados como *No Finding*.

Los términos de NIH permiten el uso de las imágenes y exigen enlazar al sitio original, acreditar al NIH Clinical Center y citar Wang et al. (CVPR 2017). Fuentes: [NIH](https://nihcc.app.box.com/v/ChestXray-NIHCC) y [condiciones resumidas por Google Cloud](https://docs.cloud.google.com/healthcare-api/docs/resources/public-datasets/nih-chest). Los PNG concretos proceden de [un espejo público S3 documentado por sus investigadores](https://doi.org/10.1101/2025.10.25.25338784); su hash no se ha cotejado con el archivo original del NIH.

## Selección y etiquetas

- 5 con etiqueta `Pneumothorax`.
- 5 con etiqueta `Effusion`.
- 5 con etiqueta `Consolidation`.
- 5 con etiqueta `No Finding` (no equivale a certificar ausencia de enfermedad).

La selección es **intencional y equilibrada**, con pacientes distintos dentro de esta muestra. No es representativa de un hospital, no utiliza adjudicación diagnóstica individual y no se ha diseñado para calcular métricas clínicas.

## Descarga y consulta

- [Galería de las 20 radiografías y puntuaciones](../examples/nih/README.md)
- [Archivos PNG originales de la muestra](../examples/nih/radiografias/)
- [Manifiesto con hash y fuente por imagen](NF3_NIH_20_MANIFEST.json)
- [CSV completo de puntuaciones](NF3_NIH_20_RESULTADOS.csv)
- [Resumen automatizado](NF3_NIH_20_RESUMEN.json)
- [Script que permite repetir la selección y evaluación](../scripts/validacion_nih.py)

## Experimento ejecutado

El motor fue TorchXRayVision `densenet121-res224-nih`. Se ejecutaron 20 inferencias; las pruebas técnicas registraron 20 PDFs y 20 mapas Grad-CAM generados. El lote se analizó sobre una revisión anterior a las mejoras visuales del informe final, con el mismo adaptador del modelo.

Puntuaciones medias **sin calibración** en los casos que tienen cada etiqueta frente a los otros 15 casos:

| Salida del modelo | Media: grupo con etiqueta | Media: otras 15 imágenes |
|---|---:|---:|
| Neumotórax | 0,197106 | 0,046805 |
| Derrame pleural | 0,141804 | 0,138916 |
| Consolidación | 0,057116 | 0,051763 |

La separación entre grupos es débil en derrame y consolidación; no se oculta este resultado. Las puntuaciones no deben expresarse como porcentajes de acierto, certeza ni prioridad asistencial.

## Límites experimentales

1. El checkpoint ya fue entrenado en el dominio NIH; la selección del *test_list.txt* no demuestra independencia respecto al entrenamiento anterior.
2. Las etiquetas se extrajeron de informes con NLP y pueden contener errores.
3. El número de imágenes es demasiado pequeño y su distribución está controlada artificialmente.
4. Grad-CAM muestra patrones de activación, no zonas de lesión verificadas.
5. La procedencia de los bytes reproducidos se documenta con hash y URL del espejo, sin certificar equivalencia exacta con el origen primario.

**Cita:** Wang, X. y colaboradores. *ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases*, CVPR (2017), DOI 10.1109/CVPR.2017.369. Datos proporcionados por el NIH Clinical Center.
