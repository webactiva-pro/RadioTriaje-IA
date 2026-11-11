@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title TrIA - Grupo 8

echo ===================================================
echo TrIA - Inicio local
echo ===================================================

set "PY_CMD="
py -3.11 --version >nul 2>&1
if not errorlevel 1 set "PY_CMD=py -3.11"
if not defined PY_CMD (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3.13"
)
if not defined PY_CMD (
    echo [ERROR] Instale Python 3.11 o 3.13 para usar la IA.
    goto :fail
)

rem Entorno exclusivo del lanzador; no reutiliza .venv de Python 3.14.
set "VENV_PY=.venv-tria\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [1/4] Creando entorno compatible...
    %PY_CMD% -m venv .venv-tria
    if errorlevel 1 goto :fail
) else (
    echo [1/4] Entorno compatible existente.
)
"%VENV_PY%" -c "import sys; assert sys.version_info[:2] in ((3,11),(3,13))"
if errorlevel 1 (
    echo [ERROR] El entorno .venv-tria no tiene Python 3.11 o 3.13.
    echo Renombre .venv-tria a .venv-tria-antiguo y repita.
    goto :fail
)

echo [2/4] Instalando dependencias de la aplicacion...
"%VENV_PY%" -m pip install -r environment\requirements-dev.txt
if errorlevel 1 goto :fail
"%VENV_PY%" -m pip install -e . --no-deps
if errorlevel 1 goto :fail

if /I "%~1"=="demo" (
    set "TRIA_MODEL_BACKEND=demo"
    echo [3/4] Prueba tecnica sin IA.
) else (
    set "TRIA_MODEL_BACKEND=xrv"
    echo [3/4] Preparando IA preentrenada en CPU...
    "%VENV_PY%" -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.10.0 torchvision==0.25.0
    if errorlevel 1 goto :fail
    "%VENV_PY%" -m pip install -r environment\requirements-ml.txt
    if errorlevel 1 goto :fail
)

echo [4/4] Generando imagen artificial de prueba...
"%VENV_PY%" scripts\generar_imagen_demo.py
if errorlevel 1 goto :fail

echo.
echo Motor: %TRIA_MODEL_BACKEND%
echo Abrir: http://127.0.0.1:8000
echo Detener con Ctrl+C.
echo.
start "" "http://127.0.0.1:8000"
"%VENV_PY%" -m uvicorn tria.api:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto :fail
goto :end

:fail
echo.
echo Inicio interrumpido; revise el error anterior.
:end
pause
endlocal
