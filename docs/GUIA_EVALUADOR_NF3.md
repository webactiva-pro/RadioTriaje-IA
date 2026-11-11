# Guía de evaluación — TrIA, Grupo 8, NF3

**Acceso:** repositorio público, no necesita usuario de GitHub ni invitación.

## 1. Revisión sin instalar nada

1. Lea la **memoria académica** entregada en Blackboard, que contiene portada, alcance, arquitectura, resultados y referencias.
2. Consulte [el código fuente público](https://github.com/webactiva-pro/RadioTriaje-IA) y la [estructura del programa](../src/tria).
3. Abra [GitHub Actions](https://github.com/webactiva-pro/RadioTriaje-IA/actions) para revisar la ejecución real de pytest, Chromium y del modelo preentrenado. Las capturas del navegador y el PDF de una ejecución sintética están disponibles en los artefactos de sus workflows, mientras dure su retención.
4. Revise el [manifiesto NIH](NF3_NIH_20_MANIFEST.json), los [resultados del lote](NF3_NIH_20_RESULTADOS.csv) y la [matriz de implementación NF2→NF3](NF3_ESTADO_IMPLEMENTACION.md). El lote es descriptivo, no una validación diagnóstica independiente.

## 2. Si desea ejecutarlo en Windows

Requisitos: Git, Python 3.11 o 3.13 y conexión a Internet. En CMD:

```cmd
cd /d "%USERPROFILE%"
git clone https://github.com/webactiva-pro/RadioTriaje-IA.git RadioTriaje-NF3-evaluacion
cd RadioTriaje-NF3-evaluacion
iniciar_tria_windows.cmd
```

Abra `http://127.0.0.1:8000`, cargue `data/demo_geometrico.png`, pulse **Cargar imagen** y después **Ejecutar análisis**. Compruebe que aparece `EXPLORATORIO`, que se genera el PDF y que el estudio puede reabrirse desde el historial. El patrón artificial no permite medir rendimiento clínico.

Se necesita descargar los pesos del modelo en el primer análisis. Para pruebas de integración sin IA se puede ejecutar `iniciar_tria_windows.cmd demo`, opción reservada al desarrollo.

## 3. Qué ha sido validado y qué no

Los workflows comprueban instalación de dependencias, contratos HTTP, persistencia, manejo de errores, informe PDF, navegador y ejecución técnica de DenseNet-121 con pesos reales. No acreditan sensibilidad diagnóstica, triaje clínico, privacidad médica completa ni cumplimiento regulatorio. El modelo externo y el uso de herramientas de IA se atribuyen en el README.

**Procedencia de esta copia:** exportación limpia y seleccionada de los archivos técnicos de NF3. No se ha importado el historial del fork privado, ni los PDF anteriores del grupo, ni imágenes originales, ni pesos de modelo.
