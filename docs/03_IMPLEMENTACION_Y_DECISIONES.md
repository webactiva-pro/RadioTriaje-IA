# 03 · Implementación, decisiones y trabajo pendiente

## Decisiones técnicas aplicadas

| Decisión | Motivo | Evidencia o consecuencia |
|---|---|---|
| API con FastAPI | API local simple y OpenAPI automática | `api.py`, tests de endpoints |
| SQLite + SQLAlchemy | Persistencia reproducible sin servidor de BBDD | `database.py`, tests de reinicio y migración |
| Modelo TorchXRayVision NIH | Disponer de una inferencia real sin entrenamiento propio ficticio | `inference.py`, smoke con pesos reales |
| `demo` como modo de pruebas | Poder validar API/SQLite/UI sin descargar PyTorch | Test E2E separado; no es el arranque de usuario |
| Grad-CAM | Visualizar activaciones para una clase; sin afirmar localización de patología | `gradcam.py`, imagen en PDF |
| Informe con hashes | Relacionar archivo importado, análisis, pesos y revisión del código | `report.py`, tests PDF y persistencia |
| Identificar fuentes por SHA | Evitar fiarse del nombre de fichero o afirmar autorías de una imagen desconocida | `provenance.py` y manifiesto NIH |
| Lanzador Windows con IA predeterminada | Evitar iniciar accidentalmente sin el modelo | `iniciar_tria_windows.cmd` y tests del README |

## Registro de cambios por fase

- **Fase 0:** viabilidad y responsabilidades propuestas; no se afirmaba tener software funcional.
- **NF2:** proyecto diseñado con requisitos RF01–RF09, siete entidades lógicas previstas, riesgos y backlog de diez historias de usuario. Los detalles aún no implementados se reflejan en la matriz de requisitos.
- **NF3:** aplicación local operativa, simplificación del esquema de datos y sustitución del entrenamiento planificado por un checkpoint académico preentrenado; controles de origen, hashes, tests e informes.
- **Publicación de evaluación:** copia pública independiente y limpia, sin historial de fork ni documentos personales previos. El código es equivalente a la revisión probada de NF3; workflows ejecutados en el repositorio público.

## Diseño original: decisiones que no consta ratificar formalmente

En NF2 quedaron pendientes la asignación definitiva de roles, el origen complementario de datos, reglas y umbrales experimentales de prioridad, protocolo de entrenamiento, métricas con etiquetas fiables, calendario de integración en el repositorio oficial y aceptación del documento grupal. Esta documentación no las convierte retroactivamente en acuerdos cerrados.

## Aspectos pendientes y límites

1. **Evaluación clínica:** no existen métricas de sensibilidad, especificidad, AUROC/AUPRC ni calibración clínicamente verificadas.
2. **Priorización:** no hay etiquetas de urgencia ni reglas aceptadas para asignar prioridades. La aplicación se abstiene.
3. **Privacidad:** se rechazan metadatos identificativos habituales, pero no se garantiza ausencia de texto incrustado en píxeles.
4. **Origen de datos:** las 20 imágenes se obtuvieron de un espejo de la colección NIH. Se conserva el SHA del espejo, no una prueba de igualdad bit a bit con el NIH oficial.
5. **Cobertura DICOM:** limitada a radiografías monocromáticas CR/DX con codificación admitida por pydicom.
6. **Entorno:** no hay autenticación multiusuario, PACS/HIS, despliegue productivo, GPU necesaria ni monitorización hospitalaria.
7. **Publicación de documentos históricos:** no se distribuyen PDF de fases anteriores con datos de los integrantes; esta reconstrucción técnica indica las decisiones y limitaciones relevantes.

## Qué evidencia cada parte

- **Código:** implementaciones comprobables en módulos.
- **Tests:** comportamiento de la API e interfaz con datos sintéticos, integración del modelo con pesos reales.
- **Ejemplos NIH:** imágenes y salidas reproducibles, pero NO estudio clínico ni prueba de generalización.
- **Memoria NF3:** documentación entregada en Blackboard por el grupo, asociada al commit de evaluación.
