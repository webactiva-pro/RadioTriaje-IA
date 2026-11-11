# 01 · Contexto y evolución del proyecto

## Punto de partida: Fase 0

**TrIA (RadioTriaje-AI)** se concibió como un proyecto académico para estudiar si es viable combinar procesamiento de radiografías torácicas, clasificación de hallazgos por aprendizaje profundo, explicaciones visuales y una interfaz que permita seguir cada ejecución.

La propuesta inicial distribuía las responsabilidades entre cuatro áreas: datos y calidad, modelos y evaluación, API y persistencia, e interfaz y presentación. El reparto concreto de personas variaba entre fuentes iniciales y quedó sujeto a revisión del grupo; por eso esta copia pública no atribuye de forma individual desarrollos ni decisiones posteriores.

**Estado histórico:** Fase 0 correspondía a presentación y viabilidad, no a una aplicación ya funcionando. En la auditoría de NF2 se documentaron dos versiones de su PDF (6 y 10 páginas); no existe evidencia suficiente aquí para afirmar cuál quedó aprobada como única versión final. Ambas se conservan fuera de esta copia pública.

## NF2 — Documentación y diseño técnico (octubre de 2026)

La fase de diseño consolidó una arquitectura y un alcance propuesto. Sus 14 apartados cubrían descripción funcional, objetivos, arquitectura, tecnologías, datos, modelo ER, fuentes NIH/RSNA, accesibilidad, RGPD, diez historias de usuario, organización, riesgos, pruebas y referencias.

### Flujo previsto

1. Importar una imagen autorizada PNG o DICOM.
2. Verificar formato, tamaño, calidad y metadatos relevantes.
3. Registrar un estudio identificable por su huella y un ID técnico.
4. Ejecutar un clasificador multietiqueta DenseNet-121.
5. Generar una representación Grad-CAM de activaciones.
6. Calcular, en una versión futura, una **señal de prioridad de demostración** a partir de reglas versionadas, con abstención ante errores. La fase de diseño no aportaba etiquetas de referencia de urgencia asistencial.
7. Consultar resultados e historial; exportar un informe PDF.
8. Evaluar el sistema mediante métricas reales y un protocolo de datos separado por pacientes cuando corresponda.

Los requisitos originales RF01–RF09 y su estado final pueden verse en [Diseño y arquitectura](02_DISENO_Y_ARQUITECTURA.md).

### Datasets previstos

- **NIH ChestX-ray14:** principal candidato para clasificación multietiqueta; etiquetas derivadas de informes mediante procesamiento de lenguaje natural.
- **RSNA Pneumonia Detection Challenge:** propuesta complementaria para trabajar con DICOM y cajas de localización, no integrada en NF3.
- Una tercera fuente JPEG mencionada en Fase 0 quedó sin identificar suficientemente y no se utilizó.

**Estado al terminar NF2:** se había diseñado la solución; no existían entrenamiento propio ni aplicación funcional acreditados. El diseño no debe presentarse retrospectivamente como una entrega de software ya ejecutada.

## NF3 — Producto funcional y reproducible (noviembre de 2026)

NF3 llevó una parte de ese diseño a código, priorizando un flujo local verificable y reproducible:

- FastAPI y validación de imágenes PNG/JPEG y DICOM CR/DX monocromático.
- SQLite para estudios, análisis, huellas y auditoría.
- Interfaz web para cargar imágenes, revisar resultados, recuperar estudios e informes.
- Integración de un **modelo externo preentrenado** de TorchXRayVision (DenseNet-121 NIH), con tres salidas: neumotórax, derrame pleural y consolidación.
- Grad-CAM experimental, PDF con ambas imágenes cuando existan, hashes y datos de ejecución.
- Pruebas automáticas en Python 3.11/3.13, navegador Chromium y smoke de IA real.
- Ensayo exploratorio con 20 imágenes etiquetadas del NIH, sin reclamar validación médica independiente.

### Decisiones de alcance

El grupo no llegó a entrenar y evaluar desde cero un clasificador con separación independiente y métricas clínicas fiables. La simulación de prioridad del diseño tampoco se convirtió en un algoritmo con umbrales validados; la aplicación se abstiene de asignar urgencia. Para un proyecto de Fase 2 funcional, se documentó la diferencia en lugar de mostrar cifras fabricadas.

## Evolución resumida

| Hito | Diseño o resultado | Evidencia |
|---|---|---|
| Fase 0 | Idea y estudio de viabilidad | Referencias históricas del grupo |
| NF2 | Arquitectura, RF01–RF09, datos y plan de pruebas | Diseño técnico consolidado de octubre, sintetizado en esta documentación |
| NF3 | Aplicación local, modelo preentrenado, historial e informes | Código, tests y [Actions](https://github.com/webactiva-pro/RadioTriaje-IA/actions) |
| Muestra NIH | 20 PNG con etiquetas, hashes y tres puntuaciones por caso | [Radiografías y resultados](../examples/nih/README.md) |

**Límites de la reconstrucción:** no se declara que todos los cambios se aprobaran formalmente por el equipo. Las memorias grupales antiguas no se han copiado a GitHub público porque incluyen información personal y versiones históricas cuya validez debe ratificarse.
