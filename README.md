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

## Estado

Actividad 0: identificacion del proyecto, descarga y revision inicial del dataset.
