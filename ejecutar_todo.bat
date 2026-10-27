@echo off
echo ==============================================================================
echo REPRODUCCION DEL PROYECTO: CLASIFICACION AUTOMATICA DE VARIEDADES DE FRIJOL
echo ECBD Recursamiento 2026 - Kevin Hernandez Trejo (23300950)
echo ==============================================================================

echo.
echo [1/3] Ejecutando Pipeline ETL (Extraccion, Limpieza, Deduplicacion)...
.venv\Scripts\python.exe src\etl.py
if %ERRORLEVEL% NEQ 0 (
    echo Error durante el ETL.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Entrenando y evaluando modelos supervisados (Regresion y Clasificacion)...
.venv\Scripts\python.exe src\modelos_supervisados.py
if %ERRORLEVEL% NEQ 0 (
    echo Error durante el entrenamiento.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Generando evidencias graficas en outputs/...
.venv\Scripts\python.exe src\generar_graficas.py
if %ERRORLEVEL% NEQ 0 (
    echo Error generando graficas.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo PROCESO COMPLETADO EXITOSAMENTE
echo Dataset procesado en data/processed/
echo Modelos serializados en modelos/
echo Graficos y metricas guardados en outputs/
echo ==============================================================================
pause
