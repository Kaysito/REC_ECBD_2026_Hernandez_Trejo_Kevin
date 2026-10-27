# Reporte Tecnico de Unidad II: Preparacion de Datos, Calidad y Data Mart

**Asignatura:** Extraccion de Conocimiento en Bases de Datos (ECBD)  
**Modalidad:** Recursamiento 2026  
**Estudiante:** Kevin Hernandez Trejo (Matricula: 23300950)  
**Grupo:** 10IDGS-G1  
**Docente:** Ing. Jose Luis Herrera Gallardo, MTI  
**Fecha:** 16 de octubre de 2026  

---

## 1. Introduccion y Objetivos de la Unidad II

La Unidad II de la metodologia CRISP-DM comprende la **Comprension de los Datos** y la **Preparacion de los Datos (ETL)**. El objetivo principal consiste en transformar el conjunto de datos crudo (`data/raw/`) en un repositorio curado y reproducible (`data/processed/`), garantizando integridad referencial, ausencia de duplicados, consistencia tipologica y un esquema de almacenamiento dimensional (Data Mart en SQL Server) apto para el modelado supervisado y la explotacion analitica en Power BI.

---

## 2. Diccionario de Datos Exhaustivo

El conjunto cuenta con **17 atributos** (16 medidas biometricas continuas/enteras obtenidas por vision por computadora y 1 atributo categorico de variedad). A continuacion se detalla la ficha tecnica con nombres normalizados:

| No. | Atributo Original | Atributo Normalizado | Tipo Python | Tipo SQL Server | Unidad / Escala | Definicion Morfologica | Rol Analitico |
|:---:|:---|:---|:---:|:---:|:---:|:---|:---:|
| 1 | `Area` | `Area` | `int64` | `INT` | Pixeles ($px^2$) | Area interna delimitada por el contorno del grano. | Predictor / Objetivo Regresion |
| 2 | `Perimeter` | `Perimeter` | `float64` | `FLOAT` | Pixeles ($px$) | Longitud del perimetro o circunferencia del contorno. | Predictor continuo |
| 3 | `MajorAxisLength` | `MajorAxisLength` | `float64` | `FLOAT` | Pixeles ($px$) | Longitud del eje mayor de la elipse equivalente. | Predictor continuo |
| 4 | `MinorAxisLength` | `MinorAxisLength` | `float64` | `FLOAT` | Pixeles ($px$) | Longitud del eje menor perpendicular al eje mayor. | Predictor continuo |
| 5 | `AspectRation` | `AspectRatio` | `float64` | `FLOAT` | Adimensional | Razon de alargamiento $K = L / l$ (eje mayor / eje menor). | Predictor continuo |
| 6 | `Eccentricity` | `Eccentricity` | `float64` | `FLOAT` | $[0, 1)$ | Excentricidad de la elipse equivalente (0 = circulo). | Predictor continuo |
| 7 | `ConvexArea` | `ConvexArea` | `int64` | `INT` | Pixeles ($px^2$) | Area del poligono convexo envolvente minimo. | Predictor continuo |
| 8 | `EquivDiameter` | `EquivDiameter` | `float64` | `FLOAT` | Pixeles ($px$) | Diametro de un circulo equivalente: $\sqrt{4A/\pi}$. | Predictor continuo |
| 9 | `Extent` | `Extent` | `float64` | `FLOAT` | $(0, 1]$ | Razon entre el area del grano y su bounding box rectangular. | Predictor continuo |
| 10 | `Solidity` | `Solidity` | `float64` | `FLOAT` | $(0, 1]$ | Solidez o convexidad: $Area / ConvexArea$. | Predictor continuo |
| 11 | `roundness` | `Roundness` | `float64` | `FLOAT` | $(0, 1]$ | Indice de redondez clasico: $(4\pi A) / P^2$. | Predictor continuo |
| 12 | `Compactness` | `Compactness` | `float64` | `FLOAT` | $(0, 1]$ | Indice de compacidad: $EquivDiameter / MajorAxisLength$. | Predictor continuo |
| 13 | `ShapeFactor1` | `ShapeFactor1` | `float64` | `FLOAT` | Adimensional | Primer factor de forma biometrico: $MajorAxisLength / Area$. | Predictor continuo |
| 14 | `ShapeFactor2` | `ShapeFactor2` | `float64` | `FLOAT` | Adimensional | Segundo factor de forma: $MinorAxisLength / Area$. | Predictor continuo |
| 15 | `ShapeFactor3` | `ShapeFactor3` | `float64` | `FLOAT` | Adimensional | Tercer factor de forma: $Area / ((MajorAxisLength/2)^2 \times \pi)$. | Predictor continuo |
| 16 | `ShapeFactor4` | `ShapeFactor4` | `float64` | `FLOAT` | Adimensional | Cuarto factor de forma: $Area / ((MajorAxisLength/2) \times (MinorAxisLength/2) \times \pi)$. | Predictor continuo |
| 17 | `Class` | `Class` | `object` | `VARCHAR(50)` | Categorica | Variedad botánica registrada (7 clases). | Variable Objetivo Clasificacion |

---

## 3. Reporte de Calidad y Limpieza de Datos

### 3.1. Dimensiones y Completitud
- **Instancias crudas:** 13,611 registros.
- **Valores faltantes (Missing values):** 0 en todas las columnas. No se requirio imputacion estadistica.

### 3.2. Deteccion y Depuracion de Duplicados
- **Duplicados exactos detectados:** 68 observaciones identicas en los 17 campos.
- **Hallazgo analitico:** La totalidad de las 68 filas duplicadas correspondieron a la clase `HOROZ` (la cual descendio de 1,928 registros en bruto a 1,860 registros unicos).
- **Tratamiento aplicado:** Eliminacion controlada mediante `drop_duplicates()` en el pipeline ETL para evitar que datos repetidos contaminen simultaneamente las particiones de entrenamiento y prueba (prevencion de sobreajuste optimista).
- **Instancias limpias resultantes:** **13,543 observaciones**.

### 3.3. Distribucion de Instancias por Variedad (Post-Limpieza)

| Variedad | Frecuencia Bruta | Duplicados | Frecuencia Limpia | Porcentaje | Comportamiento |
|:---|:---:|:---:|:---:|:---:|:---|
| **DERMASON** | 3,546 | 0 | **3,546** | 26.18% | Clase dominante mayoritaria |
| **SIRA** | 2,636 | 0 | **2,636** | 19.46% | Frecuencia alta |
| **SEKER** | 2,027 | 0 | **2,027** | 14.97% | Frecuencia media |
| **HOROZ** | 1,928 | 68 | **1,860** | 13.73% | Frecuencia media |
| **CALI** | 1,630 | 0 | **1,630** | 12.04% | Frecuencia media-baja |
| **BARBUNYA** | 1,322 | 0 | **1,322** | 9.76% | Frecuencia baja |
| **BOMBAY** | 522 | 0 | **522** | 3.85% | Clase minoritaria desbalanceada |
| **TOTAL** | **13,611** | **68** | **13,543** | **100.00%** | Base limpia para modelado |

---

## 4. Pipeline ETL y Trazabilidad

El script automatizado [`src/etl.py`](file:///c:/Users/crepe/Documents/Proyectos/REC_ECBD_2026_Hernandez_Trejo_Kevin/src/etl.py) ejecuta las siguientes fases con estricta trazabilidad:
1. **Extraccion:** Lectura inmutable del archivo fuente en Excel desde `data/raw/`.
2. **Transformacion:** Identificacion de duplicados exactos, eliminacion de redundancias y correccion de nombres tipograficos (`AspectRation` $\rightarrow$ `AspectRatio`, `roundness` $\rightarrow$ `Roundness`).
3. **Carga y Versionado:** Almacenamiento del conjunto limpio en `data/processed/dry_beans_cleaned.csv` y emision del reporte de auditoria `data/processed/etl_summary.json`.

---

## 5. Diseno del Data Mart Dimensional (SQL Server)

Siguiendo las pautas de la guia general para la construccion del almacen analitico, se modelo un esquema estrella implementado en [`sql/schema_datamart.sql`](file:///c:/Users/crepe/Documents/Proyectos/REC_ECBD_2026_Hernandez_Trejo_Kevin/sql/schema_datamart.sql):

```text
       +--------------------+
       |    dim_variedad    |
       +--------------------+
       | PK id_variedad     |
       |    nombre_variedad |
       |    codigo_variedad |
       +---------+----------+
                 |
                 | 1:N
                 v
       +-------------------------+         +-------------------+
       |   fact_bean_morphology  |         |     dim_tamano    |
       +-------------------------+         +-------------------+
       | PK id_grano             |         | PK id_tamano      |
       | FK id_variedad          |<--------|    categoria_tam  |
       | FK id_tamano            |   N:1   |    rango_area_min |
       | FK id_forma             |-----\   |    rango_area_max |
       |    area                 |     |   +-------------------+
       |    perimeter            |     |
       |    major_axis_length    |     |   +-------------------+
       |    ... 16 medidas ...   |     \-->|     dim_forma     |
       +-------------------------+     N:1 +-------------------+
                                           | PK id_forma       |
                                           |    categoria_forma|
                                           |    rango_aspect   |
                                           +-------------------+
```

### Componentes del Data Mart:
- **`dim_variedad`:** Catalogo maestro de las 7 especies comerciales de frijol turco.
- **`dim_tamano`:** Dimension analitica para segmentar granos en *Pequeno*, *Mediano*, *Grande* y *Muy Grande* segun el area superficial.
- **`dim_forma`:** Dimension clasificatoria segun la razon de aspecto (*Casi Esferica*, *Semi-Ovalada*, *Elongada*, *Muy Elongada*).
- **`fact_bean_morphology`:** Tabla de hechos que resguarda las 16 metricas biometricas continuas de cada observacion, con soporte para consultas OLAP e indices de aceleracion en `id_variedad`, `id_tamano`, `id_forma` y `area`.
- **Vistas optimizadas:** `vw_resumen_morfologico_variedad` y `vw_distribucion_tamano_variedad` preparadas para conectar directamente con Power BI en la Unidad V.
