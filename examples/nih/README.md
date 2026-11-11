# Radiografías NIH: muestra de 20 casos

Esta carpeta contiene **20 imágenes PNG de 1024 × 1024 píxeles** tomadas del conjunto abierto NIH ChestX-ray14 (NIH Clinical Center), las mismas utilizadas en la prueba exploratoria de TrIA. Cada imagen dispone de una etiqueta original y las tres salidas del modelo.

**Cómo probarlas:** desde la aplicación, usa **Seleccionar archivo**, abre `examples/nih/radiografias/`, elige cualquier PNG y pulsa **Cargar imagen** y **Ejecutar análisis**. No es necesario generar imágenes geométricas.

Los valores se muestran con 4 o 5 decimales para facilitar la comparación; son **puntuaciones no calibradas del clasificador**, no diagnósticos ni porcentajes de acierto. La etiqueta NIH se extrajo automáticamente de informes.

| Imagen NIH | Etiqueta NIH | Neumotórax | Derrame | Consolidación |
|---|---|---:|---:|---:|
| <a href="radiografias/00000013_011.png"><img src="radiografias/00000013_011.png" alt="Radiografía NIH 00000013_011.png" width="136"></a><div><code>00000013_011.png</code></div> | Neumotórax | 0.20600 | 0.11140 | 0.06603 |
| <a href="radiografias/00000116_012.png"><img src="radiografias/00000116_012.png" alt="Radiografía NIH 00000116_012.png" width="136"></a><div><code>00000116_012.png</code></div> | Neumotórax | 0.13853 | 0.01082 | 0.02740 |
| <a href="radiografias/00000211_023.png"><img src="radiografias/00000211_023.png" alt="Radiografía NIH 00000211_023.png" width="136"></a><div><code>00000211_023.png</code></div> | Neumotórax | 0.00211 | 0.21493 | 0.01211 |
| <a href="radiografias/00000246_008.png"><img src="radiografias/00000246_008.png" alt="Radiografía NIH 00000246_008.png" width="136"></a><div><code>00000246_008.png</code></div> | Neumotórax | 0.09080 | 0.13032 | 0.10484 |
| <a href="radiografias/00000467_013.png"><img src="radiografias/00000467_013.png" alt="Radiografía NIH 00000467_013.png" width="136"></a><div><code>00000467_013.png</code></div> | Neumotórax | 0.54809 | 0.00689 | 0.30286 |
| <a href="radiografias/00000041_006.png"><img src="radiografias/00000041_006.png" alt="Radiografía NIH 00000041_006.png" width="136"></a><div><code>00000041_006.png</code></div> | Derrame pleural | 0.06384 | 0.06664 | 0.01437 |
| <a href="radiografias/00000150_000.png"><img src="radiografias/00000150_000.png" alt="Radiografía NIH 00000150_000.png" width="136"></a><div><code>00000150_000.png</code></div> | Derrame pleural | 0.01222 | 0.00026 | 0.00360 |
| <a href="radiografias/00000181_003.png"><img src="radiografias/00000181_003.png" alt="Radiografía NIH 00000181_003.png" width="136"></a><div><code>00000181_003.png</code></div> | Derrame pleural | 0.06555 | 0.25467 | 0.08801 |
| <a href="radiografias/00000344_002.png"><img src="radiografias/00000344_002.png" alt="Radiografía NIH 00000344_002.png" width="136"></a><div><code>00000344_002.png</code></div> | Derrame pleural | 0.04363 | 0.33137 | 0.05914 |
| <a href="radiografias/00000398_001.png"><img src="radiografias/00000398_001.png" alt="Radiografía NIH 00000398_001.png" width="136"></a><div><code>00000398_001.png</code></div> | Derrame pleural | 0.00185 | 0.05608 | 0.01168 |
| <a href="radiografias/00000032_016.png"><img src="radiografias/00000032_016.png" alt="Radiografía NIH 00000032_016.png" width="136"></a><div><code>00000032_016.png</code></div> | Consolidación | 0.02583 | 0.46084 | 0.02962 |
| <a href="radiografias/00000468_034.png"><img src="radiografias/00000468_034.png" alt="Radiografía NIH 00000468_034.png" width="136"></a><div><code>00000468_034.png</code></div> | Consolidación | 0.00039 | 0.00384 | 0.00200 |
| <a href="radiografias/00000583_012.png"><img src="radiografias/00000583_012.png" alt="Radiografía NIH 00000583_012.png" width="136"></a><div><code>00000583_012.png</code></div> | Consolidación | 0.00657 | 0.30921 | 0.04469 |
| <a href="radiografias/00001006_011.png"><img src="radiografias/00001006_011.png" alt="Radiografía NIH 00001006_011.png" width="136"></a><div><code>00001006_011.png</code></div> | Consolidación | 0.18527 | 0.02997 | 0.10084 |
| <a href="radiografias/00001170_010.png"><img src="radiografias/00001170_010.png" alt="Radiografía NIH 00001170_010.png" width="136"></a><div><code>00001170_010.png</code></div> | Consolidación | 0.16321 | 0.02352 | 0.10843 |
| <a href="radiografias/00000092_000.png"><img src="radiografias/00000092_000.png" alt="Radiografía NIH 00000092_000.png" width="136"></a><div><code>00000092_000.png</code></div> | No Finding | 0.05335 | 0.63748 | 0.02222 |
| <a href="radiografias/00000149_000.png"><img src="radiografias/00000149_000.png" alt="Radiografía NIH 00000149_000.png" width="136"></a><div><code>00000149_000.png</code></div> | No Finding | 0.00240 | 0.02209 | 0.00411 |
| <a href="radiografias/00000193_000.png"><img src="radiografias/00000193_000.png" alt="Radiografía NIH 00000193_000.png" width="136"></a><div><code>00000193_000.png</code></div> | No Finding | 0.01936 | 0.04131 | 0.01566 |
| <a href="radiografias/00000218_002.png"><img src="radiografias/00000218_002.png" alt="Radiografía NIH 00000218_002.png" width="136"></a><div><code>00000218_002.png</code></div> | No Finding | 0.04325 | 0.05257 | 0.02779 |
| <a href="radiografias/00000312_000.png"><img src="radiografias/00000312_000.png" alt="Radiografía NIH 00000312_000.png" width="136"></a><div><code>00000312_000.png</code></div> | No Finding | 0.01535 | 0.02855 | 0.01662 |

## Procedencia y verificabilidad

- Los originales del conjunto son del **NIH Clinical Center**. [Descarga oficial](https://nihcc.app.box.com/v/ChestXray-NIHCC).
- Los PNG de esta muestra se obtuvieron de un **espejo S3 de investigadores**. Las URLs y los **SHA-256 de los bytes descargados** están en [`docs/NF3_NIH_20_MANIFEST.json`](../../docs/NF3_NIH_20_MANIFEST.json); no se verificó identidad binaria respecto al original del NIH.
- Las etiquetas y los resultados completos están en [`docs/NF3_NIH_20_RESULTADOS.csv`](../../docs/NF3_NIH_20_RESULTADOS.csv) y el resumen de las 20 ejecuciones en [`docs/NF3_NIH_20_RESUMEN.json`](../../docs/NF3_NIH_20_RESUMEN.json).
- Puede repetirse la descarga y evaluación con [`scripts/validacion_nih.py`](../../scripts/validacion_nih.py), con PyTorch/TorchXRayVision y red disponibles.
- Las 20 imágenes ya pertenecen a un dataset público; no se incluyen radiografías privadas facilitadas por usuarios ni información clínica nueva.

## Créditos y uso

Datos del **NIH Clinical Center**. Citar: Wang et al. *ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases*, CVPR 2017, DOI [10.1109/CVPR.2017.369](https://doi.org/10.1109/CVPR.2017.369). Los términos NIH permiten el uso de las imágenes con atribución. [Información sobre las condiciones de acceso](https://docs.cloud.google.com/healthcare-api/docs/resources/public-datasets/nih-chest).

La etiqueta *No Finding* no equivale a garantizar una radiografía normal. Las puntuaciones obtenidas con un checkpoint entrenado en NIH y una muestra reducida **no constituyen validación clínica ni externa**.
