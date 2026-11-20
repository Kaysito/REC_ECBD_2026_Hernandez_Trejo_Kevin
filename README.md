# Clasificacion automatica y analisis morfologico de variedades de frijol

Proyecto individual de recursamiento para la asignatura Extraccion de Conocimiento en Bases de Datos (ECBD).

## Estudiante

- **Nombre:** Kevin Hernandez Trejo
- **Matricula:** 23300950
- **Grupo y carrera:** 10IDGS-G1
- **Docente:** Ing. Jose Luis Herrera Gallardo, MTI
- **Institucion:** Universidad Tecnologica de Tula-Tepeji (UTTT)

---

## Dataset

- **Nombre:** Dry Bean Dataset
- **Fuente:** UCI Machine Learning Repository
- **DOI:** [10.24432/C50S4B](https://doi.org/10.24432/C50S4B)
- **Registros crudos:** 13,611
- **Registros limpios:** 13,543 (68 duplicados exactos tratados en la clase `HOROZ`)
- **Variables predictoras:** 16 biometricas
- **Variable de clase:** `Class` (7 variedades botánicas)

El archivo original se conserva sin modificaciones en `data/raw`. Los datos curados se encuentran en `data/processed/dry_beans_cleaned.csv`.

---

## Estructura del Repositorio

```text
├── data/
│   ├── raw/             Datos originales inmutables (ZIP, XLSX, ARFF)
│   └── processed/       Datos limpios (dry_beans_cleaned.csv, etl_summary.json)
├── notebooks/           Jupyter Notebooks ejecutados y reproducibles
│   ├── Hernandez_Trejo_Kevin_U2_AE1_Exploracion.ipynb
│   ├── 01_preparacion_y_etl.ipynb
│   ├── 02_modelos_supervisados.ipynb
│   └── 03_modelos_no_supervisados.ipynb
├── src/                 Codigo modular en Python
│   ├── etl.py
│   ├── modelos_supervisados.py
│   ├── modelos_no_supervisados.py
│   └── generar_graficas.py
├── sql/                 Data Mart dimensional para SQL Server
│   └── schema_datamart.sql
├── ssis/                ETL visual de Integration Services
│   └── DryBean_ETL_SSIS/ Solucion, proyecto y paquete Package.dtsx
├── powerbi/             Dashboard final PBIX/PBIT, DAX y fuentes versionables
├── data/datamart/       Copia SQLite portátil del esquema estrella
├── data/bi/             Vistas CSV listas para Power BI
├── modelos/             Modelos serializados (.joblib)
├── dashboard/           Dashboard interactivo en Streamlit
├── outputs/             Reportes, metricas y graficos analiticos (.png, .json, .pdf)
├── docs/                Documentacion tecnica y reporte de revisiones
│   ├── Hernandez_Trejo_Kevin_U2_AE1_Diagnostico.pdf
│   ├── analisis_preliminar.md
│   ├── diccionario_y_calidad_datos.md
│   ├── reporte_revision_u2_u3.md
│   └── lecciones_aprendidas_y_bitacora_tecnica.md
├── ejecutar_todo.bat     Script de ejecucion rapida en un clic
└── requirements.txt     Dependencias del entorno analitico
```

---

## Metodologia CRISP-DM y Estado Actual del Proyecto

1. **Unidad I (Comprension del Problema y Planeacion - 20%):** Completada. Documento en `outputs/` y marco comparativo IA / ML / Data Mining.
2. **Unidad II (Preparacion de Datos, ETL y Data Mart - 15%):** Completada. Pipeline ETL funcional, auditoria de 68 duplicados y 0 nulos, y esquema estrella ejecutado en SQL Server 2025 LocalDB con 13,543 hechos, tres dimensiones y cero claves invalidas.
   - **SSIS visual:** paquete de nueve tareas con recuperación completa: `PREPARE -> EXTRACT -> TRANSFORM -> cuatro dimensiones -> tabla de hechos -> VALIDATE`. Puede reconstruir las tablas eliminadas y `DimVariedad`, `DimTamano`, `DimForma` y `DimTiempo` convergen visualmente en `FactBeanMorphology`.
   - **AE1 - Exploracion y diagnostico:** notebook ejecutado e informe PDF disponibles en `notebooks/` y `docs/`.
   - El diagnostico de AE1 trabaja exclusivamente en modo lectura sobre `data/raw/` y verifica la integridad del original mediante SHA-256.
3. **Unidad III (Analisis Supervisado - 25%):** Completada con particion solicitada de **70% entrenamiento / 30% prueba** (9,480 / 4,063 registros).
   - **Regresion sobre `Area` (Sin variables derivadas):**
     - Regresion Lineal: $R^2 = 0.9790$, $MAE = 3,138.22$ px.
     - Random Forest Regressor: $R^2 = 0.9996$, $MAE = 213.23$ px.
   - **Clasificacion Multiclase (`Class`):**
     - Regresion Logistica: Accuracy = 92.10%, **Macro F1 = 93.24%**.
     - k-NN (k=5): Accuracy = 91.66%, Macro F1 = 92.90%.
     - Random Forest Classifier: Accuracy = 91.95%, Macro F1 = 93.22%.
4. **Unidad IV (Analisis No Supervisado - 25%):** Implementada y reproducible.
   - Estandarizacion con `StandardScaler`.
   - PCA: 4 componentes conservan al menos 90% de la varianza.
   - Evaluacion K-means de k=2 a k=10 mediante codo y silhouette.
   - Mejor resultado interno: k=3, silhouette=0.4203.
   - Comparacion interpretativa con `Class`: ARI=0.2964 y NMI=0.4837; la clase no participa en el entrenamiento.
5. **Unidad V (Visualizacion y Cierre - 15%):** Dashboard integrado y verificado en Streamlit con indicadores, análisis descriptivo, regresión, clasificación, clustering, PCA, parámetros interpretables y trazabilidad. Power BI funciona como complemento descriptivo con una sola tabla analítica consultada directamente desde SQL Server, dos páginas, 19 visuales, 9 medidas DAX y filtros interactivos; el modelo estrella permanece documentado por separado en SQL Server y SQLite.

## Conclusiones y recomendaciones

### Conclusiones

1. Las mediciones morfológicas permiten clasificar las siete variedades con resultados consistentes. La regresión logística alcanzó 92.10% de exactitud y 93.24% de Macro F1 sobre el 30% reservado para prueba.
2. Random Forest estimó `Area` con `R² = 0.9996` y un error absoluto medio de 213.23 píxeles, sin utilizar variables que revelan el área mediante una fórmula directa.
3. K-Means encontró tres perfiles morfológicos con Silhouette de 0.4203. Los clusters separan principalmente granos pequeños y compactos, granos intermedios más alargados y un grupo reducido de granos muy grandes. Cuatro componentes PCA conservaron 95.00% de la varianza.

### Recomendaciones

1. Utilizar el clasificador como apoyo para una primera identificación automática y mantener revisión humana en variedades con mayor confusión, especialmente `SIRA` y `DERMASON`.
2. Incorporar nuevas muestras tomadas con condiciones de iluminación y captura diferentes antes de usar el modelo fuera del entorno del dataset. Esta validación permitirá comprobar su capacidad de generalización.

---

## Instrucciones de Reproduccion

Para ejecutar todo el flujo analitico en Windows:

1. Ejecutar el script por lotes:
   ```cmd
   ejecutar_todo.bat
   ```
2. O ejecutar individualmente:
   ```powershell
   .venv\Scripts\python.exe src/etl.py
   .venv\Scripts\python.exe src/modelos_supervisados.py
   .venv\Scripts\python.exe src/generar_graficas.py
   .venv\Scripts\python.exe src/modelos_no_supervisados.py
   ```

Para abrir el dashboard:

```powershell
.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

El navegador abrira normalmente `http://localhost:8501`. Los filtros del dashboard modifican la visualizacion, pero no reentrenan los modelos.

La pestaña **Modelos** permite explicar la ecuación de regresión, coeficientes, importancia de variables, parámetros de clasificación y centroides de clustering. Los valores también se conservan en `outputs/resumen_parametros_modelos.json` y archivos CSV asociados.

Para revisar el ETL visual, abrir `ssis/DryBean_ETL_SSIS/DryBean_ETL_SSIS.slnx` en Visual Studio y ejecutar `Package.dtsx`. La guia completa se encuentra en `docs/ssis_etl_visual.md`.

El ETL SSIS también está automatizado mediante el Programador de tareas de Windows. La tarea `ECBD_DryBean_ETL_0300` se ejecuta diariamente a las 03:00 y conserva una bitácora por ejecución. La configuración y las instrucciones se encuentran en `automatizacion/`.

Para regenerar la copia SQLite y los archivos de Power BI:

```powershell
.venv\Scripts\python.exe src\exportar_sqlite_datamart.py
```

SQL Server permanece como origen oficial; SQLite conserva las mismas dimensiones, claves foráneas e índices como respaldo portátil.

El tablero final se abre directamente desde `powerbi/Hernandez_Trejo_Kevin_Dashboard_DryBean.pbix`. La guía de demostración y respuestas para la revisión se encuentra en `docs/guia_powerbi_exposicion.md`.
