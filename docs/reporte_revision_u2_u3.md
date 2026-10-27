# Reporte de Avance Tecnico: Unidad II (100%) y Unidad III (50%)

**Asignatura:** Extraccion de Conocimiento en Bases de Datos (ECBD)  
**Modalidad:** Recursamiento 2026  
**Estudiante:** Kevin Hernandez Trejo (Matricula: 23300950)  
**Grupo:** 10IDGS-G1  
**Docente:** Ing. Jose Luis Herrera Gallardo, MTI  
**Fecha de Revision:** Octubre de 2026  

---

## 1. Resumen Ejecutivo del Avance

En cumplimiento con el calendario y la guia del Proyecto Integrador, se consolidaron los entregables correspondientes a la **Unidad II (Preparacion de datos, ETL y Data Mart - 100%)** y el hito intermedio de la **Unidad III (Analisis supervisado: Modelos de regresion y clasificacion funcionando - 50%)**.

```text
+---------------------------------------------------------------------------------+
|                               ESTADO DEL PROYECTO                               |
+---------------------------------------------------------------------------------+
| [X] Unidad I   (20%): Planeacion, CRISP-DM y Marco Conceptual        (Completada)|
| [X] Unidad II  (15%): ETL, Calidad, Limpieza y Data Mart SQL         (Completada)|
| [X] Unidad III (25%): Regresion y Clasificacion Funcionando          (50% Avance)|
| [ ] Unidad IV  (25%): Clustering y Reduccion de Dimensionalidad      (Pendiente) |
| [ ] Unidad V   (15%): Dashboard Power BI y Cierre                    (Pendiente) |
+---------------------------------------------------------------------------------+
```

---

## 2. Unidad II: Preparacion de Datos y Data Mart (100%)

### 2.1. Resultados del Pipeline ETL (`src/etl.py`)
- **Conjunto Original:** 13,611 filas y 17 columnas conservadas en `data/raw/dry_bean_dataset/.../Dry_Bean_Dataset.xlsx`.
- **Completitud:** 0 valores faltantes (100% de integridad).
- **Deteccion y Tratamiento de Duplicados:** Se detectaron y eliminaron **68 registros duplicados exactos**, todos pertenecientes a la variedad `HOROZ` (reduciendose de 1,928 a 1,860 registros).
- **Base Curada:** **13,543 observaciones** limpias exportadas a `data/processed/dry_beans_cleaned.csv`.
- **Estandarizacion:** Correccion de nombres de columnas (`AspectRation` $\rightarrow$ `AspectRatio`, `roundness` $\rightarrow$ `Roundness`).

### 2.2. Data Mart Dimensional (`sql/schema_datamart.sql`)
- Diseno en **esquema estrella** compatible con SQL Server:
  - **Tabla de Hechos:** `fact_bean_morphology` (16 descriptores morfologicos continuos por grano).
  - **Dimensiones:** `dim_variedad` (catalogo de 7 especies), `dim_tamano` (segmentacion de superficie) y `dim_forma` (alargamiento/redondez).
  - Vistas analiticas (`vw_resumen_morfologico_variedad` y `vw_distribucion_tamano_variedad`) listas para explotacion OLAP y conexion con Power BI.

---

## 3. Unidad III: Modelos Supervisados Funcionando (50%)

### 3.1. Regresion: Estimacion de la Variable Continua `Area`
Para evitar la fuga de informacion (*data leakage*):
1. Se excluyo `EquivDiameter` debido a que es una transformacion directa y determinista del area ($\sqrt{4A/\pi}$).
2. Se controlo `ConvexArea` por redundancia con el contorno envolvente.
3. Se utilizaron 13 descriptores geometricos independientes de perimetro, ejes y factores de forma.

| Modelo de Regresion | $R^2$ (Varianza explicada) | MAE (Error Absoluto Medio) | RMSE (Raiz Error Cuad. Medio) |
|:---|:---:|:---:|:---:|
| **Regresion Lineal Multiple (Baseline)** | 0.9987 | 776.42 px | 1,073.06 px |
| **Random Forest Regressor** | **0.9997** | **195.95 px** | **548.26 px** |

*Conclusion:* El modelo no lineal Random Forest reduce el error absoluto medio a solo 195.95 pixeles, demostrando una precision sobresaliente sin emplear variables triviales.

### 3.2. Clasificacion Multiclase: Reconocimiento de Variedades (`Class`)
Dado el desbalance entre la clase mayoritaria (`DERMASON` con 3,546) y la minoritaria (`BOMBAY` con 522), se aplico una **particion estratificada 80/20** y se priorizo la metrica **Macro F1-Score**.

| Clasificador | Accuracy | **Macro F1-Score** | Weighted F1-Score | Estado |
|:---|:---:|:---:|:---:|:---:|
| **Regresion Logistica (Multinomial)** | 91.92% | 93.02% | 91.93% | Funcional |
| **k-Nearest Neighbors (k-NN, k=5)** | 91.55% | 92.70% | 91.57% | Funcional |
| **Random Forest Classifier** | **92.03%** | **93.18%** | **92.02%** | **Mejor desempeno** |

### 3.3. Hallazgos en la Matriz de Confusion
- **Clases casi perfectamente separables:** `BOMBAY` (100% precision) y `SEKER` (>95% precision) gracias a sus claras diferencias de volumen y redondez esferica.
- **Zona de mayor confusion morfologica:** Ocurre entre `SIRA` y `DERMASON`, dos variedades de grano blanco y tamano similar que comparten rangos proximos de excentricidad y solidez.

---

## 4. Guia de Explicacion Tecnica ante el Docente

Si el docente solicita justificar decisiones clave durante la revision:

1. **¿Por que eliminaste los duplicados antes de dividir los datos?**  
   *Respuesta:* Para prevenir la fuga de informacion (*data leakage*). Si un grano duplicado queda simultaneamente en entrenamiento y prueba, el modelo recordaria la observacion exacta, arrojando una evaluacion artificialmente optimista. Ademas, detectamos que los 68 duplicados provenian unicamente de la clase HOROZ.

2. **¿Por que no utilizaste `EquivDiameter` para predecir `Area` en la regresion?**  
   *Respuesta:* Porque el diametro equivalente se deriva por formula geometrica directa del area ($Ed = \sqrt{4A/\pi}$). Incluirlo provocaria una prediccion trivial e inutil para medir el impacto real de los factores de forma y ejes morfologicos.

3. **¿Por que reportas `Macro F1` ademas de `Accuracy` en la clasificacion?**  
   *Respuesta:* Porque el dataset presenta desbalance (DERMASON representa el 26.2% de los datos mientras que BOMBAY solo el 3.8%). El Accuracy favorece a las clases dominantes, mientras que el Macro F1 promedia el rendimiento clase por clase con igual peso, garantizando que el modelo sea evaluado con el mismo rigor en variedades minoritarias.

---

## 5. Evidencias Generadas en el Repositorio

- **Scripts modulares:**
  - `src/etl.py` (Proceso ETL y limpieza).
  - `src/modelos_supervisados.py` (Entrenamiento, metricas y serializacion).
  - `src/generar_graficas.py` (Generacion de figuras analiticas).
- **Notebooks ejecutables:**
  - `notebooks/01_preparacion_y_etl.ipynb`
  - `notebooks/02_modelos_supervisados.ipynb`
- **Data Mart SQL:**
  - `sql/schema_datamart.sql`
- **Modelos serializados:**
  - `modelos/regresion_lineal.joblib`
  - `modelos/random_forest_regresor.joblib`
  - `modelos/regresion_logistica.joblib`
  - `modelos/knn_classifier.joblib`
  - `modelos/random_forest_classifier.joblib`
- **Graficos de evidencia:**
  - `outputs/distribucion_clases_limpias.png`
  - `outputs/regresion_real_vs_predicho.png`
  - `outputs/matriz_confusion_multiclase.png`
  - `outputs/comparativa_metricas_clasificacion.png`
