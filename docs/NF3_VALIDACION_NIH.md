# NF3 · Muestra radiológica NIH para pruebas funcionales (no validación clínica)

**Objetivo.** Sustituir imágenes obtenidas buscando en Internet por una muestra trazable y con etiquetas de referencia. **No entrenar** modelos ni inferir utilidad clínica.

## Fuentes y permisos

- Fuente de referencia: [NIH Clinical Center, ChestXray14](https://nihcc.app.box.com/v/ChestXray-NIHCC). Imágenes desidentificadas de uso abierto **con atribución obligatoria**.
- Etiquetas CSV y división test: copias de `Data_Entry_2017_v2020.csv` y `test_list.txt` alojadas en el repositorio de datos de [alkzar90 en Hugging Face](https://huggingface.co/datasets/alkzar90/NIH-Chest-X-ray-dataset/tree/main/data). El script genera hashes de estos ficheros.
- Imágenes PNG: copia pública S3 de investigadores (no alojamiento original del NIH), documentada en un [estudio de 2025](https://doi.org/10.1101/2025.10.25.25338784). El script almacena URL exacta y SHA-256 por imagen, pero **no acredita igualdad binaria con el NIH original**.
- Cita: Wang X., Peng Y., Lu L., Lu Z., Bagheri M., Summers R., *ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases*, CVPR 2017. DOI [10.1109/CVPR.2017.369](https://doi.org/10.1109/CVPR.2017.369). Agradecimiento al NIH Clinical Center.

## Diseño de la prueba

- 5 imágenes con etiqueta exclusivamente `Pneumothorax`.
- 5 con etiqueta exclusivamente `Effusion`.
- 5 con etiqueta exclusivamente `Consolidation`.
- 5 con etiqueta `No Finding` (no significa «paciente sano»).
- Selección determinista del *test_list.txt* oficial, con pacientes distintos y sin guardar identificadores de paciente en el manifiesto exportado. Es un **muestreo intencional, no representativo**.
- Comprobación de origen, formato PNG, tamaño, SHA-256, API de carga, inferencia con pesos reales, respuesta de error, mapa Grad-CAM e informe PDF.
- Medidas: número de ejecuciones correctas, medias de puntuaciones por clase y otros hallazgos descriptivos. **No presentar porcentajes como certeza clínica, ni la muestra como evaluación independiente.**

## Comandos desde la raíz del proyecto

Para descargar **solo** las 20 imágenes y sus etiquetas, con conexión a Internet:

```cmd
.venv\Scripts\python.exe scripts\validacion_nih.py download --per-group 5
```

Para evaluar las 20 contra el modelo TorchXRayVision (requiere `iniciar_tria_windows.cmd ia` previamente para instalar las dependencias):

```cmd
.venv\Scripts\python.exe scripts\validacion_nih.py evaluate --mode xrv
```

También se puede ejecutar `python scripts/validacion_nih.py all --per-group 5` con el entorno adecuado. Los ficheros van a `data/validacion_nih/`, que está fuera de Git (`.gitignore`). Se generan `manifest.json`, `resultados_nih.csv` y `resumen_nih.json`; nunca se deben subir datos originales ni pesos al repositorio.

GitHub Actions contiene una prueba automatizada independiente (`nf3-nih-sanity.yml`) que descarga la muestra, ejecuta el modelo con pesos verificados y entrega un ZIP temporal con evidencias. **Una ejecución fallida no se debe reportar como superada.**

## Limitaciones importantes

1. El checkpoint `densenet121-res224-nih` fue entrenado con NIH; ni siquiera usar `test_list.txt` garantiza por sí solo independencia respecto de su entrenamiento previo. **No es validación externa.**
2. La mayoría de etiquetas del NIH provienen de análisis automatizado de informes, no de adjudicación radiológica caso por caso. Puede haber falsos positivos o negativos en las etiquetas.
3. Los casos se han seleccionado deliberadamente por etiqueta única: no representan distribución real de un hospital. No calcular métricas clínicas ni fijar umbrales de triaje a partir de 20 imágenes.
4. Los mapas Grad-CAM son interpretaciones visuales aproximadas; no contamos con segmentación de referencia para cuantificar su exactitud.
5. Se descargan imágenes de un espejo de terceros. Debe revisarse la procedencia de cualquier imagen y evitar muestras con texto identificativo incrustado. Mantener almacenamiento local y un uso estrictamente académico.
6. Las métricas y los resultados definitivos solo se incorporarán al PDF después de completar realmente el proceso y fijar el SHA del commit evaluable.
