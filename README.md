# Clasificacion automatica y analisis morfologico de variedades de frijol

Proyecto individual de recursamiento para la asignatura Extraccion de Conocimiento en Bases de Datos.

## Estudiante

- Nombre: Kevin Hernandez Trejo
- Matricula: 23300950
- Grupo y carrera: 10IDGS-G1
- Institucion: Universidad Tecnologica de Tula-Tepeji

## Dataset

- Nombre: Dry Bean Dataset
- Fuente: UCI Machine Learning Repository
- Enlace: https://archive.ics.uci.edu/dataset/602/dry+bean
- Registros: 13,611
- Variables predictoras: 16
- Variable de clase: `Class`

El archivo original se conserva sin modificaciones en `data/raw`. Los datos limpios o transformados se guardaran posteriormente en `data/processed`.

## Objetivos preliminares

- Clasificacion: predecir la variedad de frijol mediante `Class`, que contiene siete clases.
- Regresion: estimar `Area` mediante caracteristicas morfologicas seleccionadas. Para evitar fuga de informacion, se evaluara excluir variables derivadas directamente del area, como `ConvexArea` y `EquivDiameter`.
- Analisis no supervisado: identificar agrupamientos naturales y estudiar la separacion entre variedades mediante clustering y PCA.

## Estructura

```text
data/
  raw/          Datos originales sin modificar
  processed/    Datos limpios y transformados
notebooks/      Exploracion y modelos
src/            Codigo reutilizable
sql/            Scripts del Data Mart
modelos/        Modelos entrenados
dashboard/      Archivos de Power BI
docs/           Informes y evidencias
```

## Metodologia de trabajo

El proyecto seguira CRISP-DM mediante seis etapas iterativas:

1. Comprension del problema.
2. Comprension de los datos.
3. Preparacion de los datos.
4. Modelado.
5. Evaluacion.
6. Despliegue y comunicacion.

La evaluacion de clasificacion considerara `macro F1`, accuracy y matriz de
confusion. La regresion se evaluara con MAE, RMSE y R2. Para el analisis no
supervisado se utilizaran PCA, clustering y la metrica silhouette.

## Herramientas propuestas

- Python, pandas y NumPy para tratamiento de datos.
- Matplotlib y Seaborn para visualizacion.
- scikit-learn para pipelines, modelos y evaluacion.
- PostgreSQL y SQL para el Data Mart.
- Power BI para el dashboard final.
- Git y GitHub para trazabilidad y evidencias.

## Planeacion

El cronograma esta alineado con las entregas del recursamiento entre el 25 de
septiembre y el 20 de noviembre de 2026. La planeacion formal de la Unidad I se
encuentra en `outputs/Hernandez_Trejo_Kevin_U1_Planeacion_Recursamiento.pdf`.

## Estado

- Actividad 0: completada.
- Unidad I: planeacion formal preparada.
