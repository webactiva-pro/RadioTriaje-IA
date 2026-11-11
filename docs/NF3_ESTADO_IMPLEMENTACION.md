# TrIA · Grupo 8 · NF3 · Estado y correspondencia con NF2

**Producto:** prototipo académico local para investigación de radiografías torácicas. No es un dispositivo médico, ni realiza diagnóstico o triaje real. **No usar imágenes de pacientes.** La arquitectura de diseño anterior se resume en la matriz RF01–RF09 y en los diagramas públicos de este directorio. Los documentos grupales históricos que contienen datos personales no se redistribuyen aquí.

## Estado funcional: qué existe y cómo se ha comprobado

| Componente | Implementación | Evidencia |
|---|---|---|
| Frontend local | Carga, validación, previsualización, resultados, Grad-CAM, historial recuperable, descarga de informes | `nf3-e2e.yml`, cinco capturas y prueba de escritorio/móvil |
| API FastAPI | Salud, estudios, análisis, historial, PDF, errores 404/422 | `tests/test_nf3.py`, `nf3-tests.yml` |
| Ingesta PNG/JPEG/DICOM | PNG/JPEG y DICOM CR/DX monocromático; se normaliza a PNG, se guarda SHA del archivo original | tests de formatos, archivo inválido y DICOM sintético |
| Persistencia | SQLite/SQLAlchemy, UUID, eventos de auditoría, registros históricos, migración aditiva de SQLite anterior | tests de reinicio, lectura histórica y migración |
| Modo de pruebas (`demo`) | Estadísticas de imagen para pruebas técnicas; no utiliza IA | CI base, E2E |
| Arranque normal Windows (`xrv`) | NIH DenseNet-121 con pesos externos, tres puntuaciones orientativas | `nf3-ml-smoke.yml`, hash de pesos, flujo API |
| Grad-CAM | Superposición exploratoria con gradientes sobre clase seleccionada | prueba de mapa real y prueba unitaria con fixture PyTorch |
| PDF experimental | Dos páginas con imágenes si existen, SHA completo, versión y campos persistentes | tests de estructura, imágenes, huellas, PDF real de smoke |
| Procedencia NIH | Referencia solo cuando SHA de entrada coincide con manifiesto académico versionado | `provenance.py`, prueba de hash y manifiesto de 20 imágenes |

## Matriz RF01–RF09 del diseño NF2

| Requisito | Estado NF3 | Límites explícitos |
|---|---|---|
| RF01. Carga DICOM/PNG | **Hecho** | DICOM CR/DX monocromático, no todos los perfiles ni códecs |
| RF02. QA/metadatos | **Parcial** | Tags más habituales; no detecta con garantías PHI/PII quemada en píxeles |
| RF03. Ingesta trazable | **Hecho** | ID, fecha, formato, hash original y origen por SHA si coincide |
| RF04. ML multietiqueta | **Adaptado** | Modelo externo real, no entrenamiento propio ni calibración clínica |
| RF05. Grad-CAM | **Técnicamente hecho** | No localización anatómica validada |
| RF06. Motor de triaje | **Abstención deliberada** | `SIN_RESULTADO` siempre; etiquetas radiológicas ≠ prioridad asistencial |
| RF07. Visor/informe | **Hecho** | PDF académico, no informe radiológico oficial |
| RF08. Persistencia/auditoría | **Hecho** | SQLite local y migraciones aditivas; sin cifrado/RBAC |
| RF09. Evaluación reproducible | **Pruebas de software y muestra descriptiva** | No estimaciones fiables de AUROC/AUPRC, sensibilidad ni especificidad |

La arquitectura efectiva separa `web` (interacción), `api` (HTTP), `image_io` (QA), `inference` (motor), `gradcam` (explicación), `database` (persistencia), `provenance` (fuente por SHA) y `report` (documento PDF). La interfaz no accede directamente a la base de datos ni manipula pesos. La dependencia NIH de terceros está identificada expresamente.

## Trazabilidad mejorada y compatibilidad

1. `studies.sha256` conserva el hash **del archivo subido**. No se guarda la imagen original; el PNG normalizado puede tener bytes diferentes. `studies.provenance` registra una coincidencia con el SHA del manifiesto NIH de 20 casos o declara procedencia desconocida. No se acredita una imagen por su nombre.
2. Cada `analyses` conserva la versión de modelo, sus puntuaciones, estado, `weights_sha256` **calculado al cargar el checkpoint** si el fichero está disponible, `software_revision` si se dispone de SHA Git (añade `+dirty` cuando corresponde) y `gradcam_target` si existe mapa.
3. Un informe PDF recuperado se genera con los metadatos guardados de la ejecución histórica. No toma la revisión o hash del modelo actual para inventar lo que no quedó registrado. Campos ausentes de registros antiguos se muestran como «no registrados».
4. `database.open_database` aplica migraciones aditivas y no elimina ni reescribe tablas existentes de versiones previas. Se ha probado con una base SQLite anterior sintética.
5. El origen `NIH ChestX-ray14` se reconoce únicamente para un conjunto versionado de 20 hashes procedentes de una copia pública S3; no se ha confirmado identidad binaria respecto al original NIH. Sus etiquetas proceden de NLP, no de confirmación clínica manual.

## Limitaciones, riesgos y mitigaciones

| Riesgo | Mitigación actual | Pendiente |
|---|---|---|
| Resultado interpretado como diagnóstico | Avisos persistentes y abstención obligatoria | Validación hospitalaria/regulatoria fuera de NF3 |
| Información identificativa en DICOM o píxeles | Rechazo de tags frecuentes, sin persistir originales ni nombres | Proceso formal de anonimización y revisión de píxeles |
| Errores y sesgos de etiquetas NIH | Etiquetas citadas como NLP, muestras separadas, sin afirmaciones médicas | Validación externa autorizada con etiquetas revisadas |
| Pesos/modelo no disponibles | Estado `MODELO_NO_DISPONIBLE`, sin predicciones inventadas | Caché controlada, distribución y licencia auditadas |
| Falta de seguridad para red | Ejecutar solo en `127.0.0.1`, sin datos de pacientes | Autenticación, TLS, cifrado, roles, RGPD antes de uso real |
| Concurrencia de hooks de Grad-CAM | Bloqueo de inferencia XRV dentro del proceso | Pruebas bajo carga y despliegue multiworker |
| Ramas y dependencias cambiantes | Commit evaluable fijo, requisitos versionados, GitHub Actions | Acceso del profesor y cierre formal de grupo |

## NF4 / futuras líneas de trabajo, no acreditadas en NF3

Entrenamiento propio con datasets autorizados; splits por paciente sin fugas; validación independiente con AUROC/AUPRC, falsos negativos y calibración; análisis de sesgo por procedencia y vista; Grad-CAM contrastado con localizaciones anotadas; auditoría de licencias/privacidad, seguridad y despliegue. El nombre «RadioTriaje-AI» es histórico: **el software no prioriza pacientes**.

## Procedencia y declaración de IA

El equipo del Grupo 8 es titular del proyecto académico. ChatGPT colaboró en planteamiento del MVP, módulos Python y JavaScript, depuración, pruebas, documentación y mejoras de interfaz. El software se comprobó con [GitHub Actions públicas](https://github.com/webactiva-pro/RadioTriaje-IA/actions): pruebas Python 3.11/3.13, flujo Chromium y ejecución independiente con pesos de IA reales. La guía de reproducción es [05_EJECUCION_Y_VERIFICACION.md](05_EJECUCION_Y_VERIFICACION.md). El modelo y checkpoint utilizados proceden de Joseph P. Cohen y colaboradores (TorchXRayVision). Datos NIH del NIH Clinical Center (Wang et al., CVPR 2017). Se publican **20 radiografías NIH desidentificadas** en [`examples/nih/radiografias/`](../examples/nih/radiografias/) con atribución, etiquetas y huellas; los **pesos externos** del modelo no se incorporan al repositorio. Los archivos NIH fueron obtenidos de un espejo documentado, no cotejado binariamente con el origen oficial.
