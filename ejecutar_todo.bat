@echo off
echo ==============================================================================
echo REPRODUCCION DEL PROYECTO: CLASIFICACION AUTOMATICA DE VARIEDADES DE FRIJOL
echo ECBD Recursamiento 2026 - Kevin Hernandez Trejo (23300950)
echo ==============================================================================

echo.
echo [1/5] Ejecutando Pipeline ETL (Extraccion, Limpieza, Deduplicacion)...
.venv\Scripts\python.exe src\etl.py
if %ERRORLEVEL% NEQ 0 (
    echo Error durante el ETL.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/5] Entrenando y evaluando modelos supervisados (Regresion y Clasificacion)...
.venv\Scripts\python.exe src\modelos_supervisados.py
if %ERRORLEVEL% NEQ 0 (
    echo Error durante el entrenamiento.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/5] Generando evidencias graficas en outputs/...
.venv\Scripts\python.exe src\generar_graficas.py
if %ERRORLEVEL% NEQ 0 (
    echo Error generando graficas.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [4/5] Ejecutando PCA y K-means...
.venv\Scripts\python.exe src\modelos_no_supervisados.py
if %ERRORLEVEL% NEQ 0 (
    echo Error durante el analisis no supervisado.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [5/5] Generando Data Mart SQLite y vistas para Power BI...
.venv\Scripts\python.exe src\exportar_sqlite_datamart.py
if %ERRORLEVEL% NEQ 0 (
    echo Error generando el Data Mart SQLite.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo PROCESO COMPLETADO EXITOSAMENTE
echo Dataset procesado en data/processed/
echo Modelos serializados en modelos/
echo Graficos y metricas guardados en outputs/
echo Data Mart SQLite en data/datamart/ y vistas Power BI en data/bi/
echo Para abrir el dashboard: .venv\Scripts\python.exe -m streamlit run dashboard\app.py
echo ==============================================================================
pause
