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
│   ├── 01_preparacion_y_etl.ipynb
│   └── 02_modelos_supervisados.ipynb
├── src/                 Codigo modular en Python
│   ├── etl.py
│   ├── modelos_supervisados.py
│   └── generar_graficas.py
├── sql/                 Data Mart dimensional para SQL Server
│   └── schema_datamart.sql
├── modelos/             Modelos serializados (.joblib)
├── outputs/             Reportes, metricas y graficos analiticos (.png, .json, .pdf)
├── docs/                Documentacion tecnica y reporte de revisiones
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
2. **Unidad II (Preparacion de Datos, ETL y Data Mart - 15%):** Completada. Pipeline ETL funcional, auditoria de 68 duplicados y 0 nulos, esquema estrella en SQL Server.
3. **Unidad III (Analisis Supervisado - 25%):** Avance funcional del 50% listo para revision.
   - **Regresion sobre `Area` (Sin variables derivadas):**
     - Regresion Lineal: $R^2 = 0.9799$, $MAE = 3,112.06$ px.
     - Random Forest Regressor: $R^2 = 0.9997$, $MAE = 191.79$ px.
   - **Clasificacion Multiclase (`Class`):**
     - Regresion Logistica: Accuracy = 91.92%, Macro F1 = 93.02%.
     - k-NN (k=5): Accuracy = 91.55%, Macro F1 = 92.70%.
     - Random Forest Classifier: Accuracy = 92.03%, **Macro F1 = 93.18%**.
4. **Unidad IV (Analisis No Supervisado - 25%):** Por iniciar (Clustering k-means y PCA).
5. **Unidad V (Visualizacion y Cierre - 15%):** Por iniciar (Dashboard Power BI).

---

## Instrucciones de Reproduccion

Para ejecutar todo el flujo en Windows:

1. Ejecutar el script por lotes:
   ```cmd
   ejecutar_todo.bat
   ```
2. O ejecutar individualmente:
   ```powershell
   .venv\Scripts\python.exe src/etl.py
   .venv\Scripts\python.exe src/modelos_supervisados.py
   .venv\Scripts\python.exe src/generar_graficas.py
   ```
