# Documentación de TrIA

Esta sección reúne el recorrido desde la definición del proyecto hasta la implementación y las pruebas. Los documentos diferencian **lo diseñado**, **lo implementado** y **lo pendiente**, para evitar atribuir a NF3 funciones que solo figuraban como propuesta en NF2.

| Documento | Contenido |
|---|---|
| [01 · Contexto y fases](01_CONTEXTO_Y_FASES.md) | Origen, objetivos y evolución de Fase 0, NF2 y NF3 |
| [02 · Diseño y arquitectura](02_DISENO_Y_ARQUITECTURA.md) | Requisitos RF01–RF09, arquitectura prevista y arquitectura real |
| [03 · Implementación y decisiones](03_IMPLEMENTACION_Y_DECISIONES.md) | Cambios de alcance, módulos, alternativas, restricciones y deuda técnica |
| [04 · Datos y resultados](04_DATOS_Y_RESULTADOS.md) | NIH, selección de 20 casos, puntuaciones, métricas y limitaciones |
| [05 · Ejecución y verificación](05_EJECUCION_Y_VERIFICACION.md) | Instalación, pruebas, GitHub Actions y evidencias |
| [Muestra radiológica](../examples/nih/README.md) | Imágenes originales con tabla de resultados y SHA-256 |

### Archivos de referencia técnica

- [`arquitectura.svg`](arquitectura.svg) y [`modelo_datos.svg`](modelo_datos.svg): diagramas históricos de diseño, que no implican implementación de cada entidad prevista.
- [`NF3_ESTADO_IMPLEMENTACION.md`](NF3_ESTADO_IMPLEMENTACION.md): detalle técnico de correspondencia con NF2.
- [`NF3_VALIDACION_NIH.md`](NF3_VALIDACION_NIH.md): protocolo de muestreo y selección.
- [`NF3_NIH_20_MANIFEST.json`](NF3_NIH_20_MANIFEST.json), [`NF3_NIH_20_RESULTADOS.csv`](NF3_NIH_20_RESULTADOS.csv) y [`NF3_NIH_20_RESUMEN.json`](NF3_NIH_20_RESUMEN.json): datos reproducibles del ensayo NIH.

### Origen de esta edición

La documentación original de Fase 0 y la memoria consolidada de NF2 se conservaron en el repositorio de trabajo del grupo. Esta edición pública **sintetiza su contenido técnico sin reproducir los documentos personales originales**, y marca expresamente qué decisiones no constan ratificadas. El código público no hereda el historial del fork previo.
