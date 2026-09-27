# Analisis preliminar del Dry Bean Dataset

## Problema

El proyecto estudiara si las mediciones geometricas obtenidas de imagenes de granos permiten reconocer automaticamente la variedad de frijol. Las variedades pueden compartir rasgos visuales parecidos, por lo que una clasificacion manual puede ser lenta o inconsistente. El analisis buscara identificar las caracteristicas que mejor separan las variedades y construir modelos capaces de apoyar una clasificacion uniforme.

## Revision inicial

- 13,611 registros.
- 16 variables predictoras numericas.
- Una variable categorica objetivo, `Class`.
- Siete variedades: BARBUNYA, BOMBAY, CALI, DERMASON, HOROZ, SEKER y SIRA.
- Cero valores faltantes detectados.
- 68 filas duplicadas exactas, que deberan revisarse durante la preparacion de datos.

## Objetivos preliminares

### Clasificacion

Predecir `Class` a partir de las 16 mediciones morfologicas. Es un problema de clasificacion multiclase con siete categorias.

### Regresion

Estimar `Area` como variable continua a partir de caracteristicas de forma y dimensiones. Antes de modelar se revisara la posible fuga de informacion causada por `ConvexArea` y `EquivDiameter`, debido a su relacion directa con el area.

## Preguntas iniciales

1. ¿Que caracteristicas morfologicas permiten distinguir mejor las siete variedades de frijol?
2. ¿Con que precision puede predecirse la variedad de un grano utilizando sus mediciones geometricas?
3. ¿Existen agrupamientos naturales que coincidan con las variedades registradas o revelen perfiles morfologicos compartidos?
