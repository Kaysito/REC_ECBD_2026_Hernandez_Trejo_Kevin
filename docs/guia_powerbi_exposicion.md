# Guía de exposición del dashboard Power BI

**Proyecto:** Clasificación automática y análisis morfológico de variedades de frijol

**Estudiante:** Kevin Hernandez Trejo

**Matrícula:** 23300950

**Grupo y carrera:** 10IDGS-G1

## Qué se implementó

El dashboard de Power BI analiza los 13,543 registros limpios del Dry Bean Dataset. Contiene dos páginas, 19 elementos visuales y nueve medidas DAX. Los segmentadores permiten examinar los datos por variedad, categoría de tamaño y categoría de forma sin modificar el dataset ni reentrenar modelos.

Power BI utiliza únicamente la tabla plana `DryBean_Analitica`; no contiene modelo estrella ni relaciones. El esquema estrella sí existe como parte independiente del proyecto en SQL Server y SQLite, pero no se incorporó al archivo PBIX.

## Archivos que debes abrir

1. Abre `powerbi/Hernandez_Trejo_Kevin_Dashboard_DryBean.pbix` con Power BI Desktop.
2. Si Power BI solicita una fuente, selecciona `data/bi/drybean_powerbi.csv`.
3. Pulsa **Inicio > Actualizar** y espera a que termine.
4. Comprueba que en el panel de datos aparezca solamente `DryBean_Analitica`.
5. Recorre las páginas **Resumen ejecutivo** y **Detalle morfológico**.

El archivo `.pbit` es la plantilla reproducible. Para la exposición conviene abrir el `.pbix`, porque ya contiene los datos.

## Página 1: Resumen ejecutivo

Las cinco tarjetas presentan una lectura rápida del conjunto analítico:

- **Total Granos:** 13,543 registros después de retirar 68 duplicados exactos del original.
- **Variedades Analizadas:** siete clases de frijol.
- **Área Promedio:** aproximadamente 53,048 píxeles por grano.
- **Redondez Promedio:** aproximadamente 0.874; valores cercanos a uno indican formas más circulares.
- **Compacidad Promedio:** aproximadamente 0.800; resume qué tan compacta es la forma del grano.

La gráfica de barras compara la cantidad de muestras por variedad. La gráfica de columnas compara el área promedio de las variedades. Los tres segmentadores filtran simultáneamente tarjetas, gráficas y tabla. La tabla final permite comprobar los valores con más detalle.

## Página 2: Detalle morfológico

Esta página profundiza en la forma y el tamaño:

- Las tarjetas muestran área mínima, área máxima, perímetro promedio y solidez promedio.
- El gráfico de dona presenta la distribución de categorías de tamaño.
- El gráfico de barras presenta la distribución de categorías de forma.
- El gráfico comparativo contrasta redondez y compacidad entre variedades.
- La tabla permite revisar registros y medidas morfológicas específicas.

## Demostración sugerida frente al profesor

1. Abre el PBIX y señala que el panel de datos tiene una sola tabla analítica.
2. Muestra las cinco tarjetas y explica qué resume cada una.
3. Selecciona una variedad en el segmentador y observa cómo cambian todas las visualizaciones.
4. Agrega un filtro de tamaño o forma para demostrar la interacción entre filtros.
5. Limpia los filtros con el icono de borrador del segmentador.
6. Abre la segunda página y compara área, perímetro, redondez, compacidad y solidez.
7. Aclara que el tablero describe y filtra resultados; no reentrena los modelos de Machine Learning.
8. Explica que el Data Mart estrella existe en SQL Server/SQLite, pero por decisión de diseño no se agregó a Power BI.

## Medidas DAX principales

```DAX
Total Granos = COUNTROWS(DryBean_Analitica)
Variedades Analizadas = DISTINCTCOUNT(DryBean_Analitica[variedad])
Area Promedio = AVERAGE(DryBean_Analitica[area])
Redondez Promedio = AVERAGE(DryBean_Analitica[roundness])
Compacidad Promedio = AVERAGE(DryBean_Analitica[compactness])
Area Minima = MIN(DryBean_Analitica[area])
Area Maxima = MAX(DryBean_Analitica[area])
Perimetro Promedio = AVERAGE(DryBean_Analitica[perimeter])
Solidez Promedio = AVERAGE(DryBean_Analitica[solidity])
```

Las medidas se recalculan automáticamente con el contexto de filtro. Por eso una tarjeta cambia cuando se selecciona una variedad, tamaño o forma.

## Diez preguntas probables y respuestas

1. **¿Cuál es el objetivo del dashboard?**

   Resumir y comparar las características morfológicas de siete variedades de frijol mediante indicadores, filtros y visualizaciones interactivas.

2. **¿Cuántos datos utiliza?**

   Utiliza 13,543 registros limpios. El archivo original tenía 13,611 y se identificaron 68 duplicados exactos.

3. **¿El dashboard modifica el dataset original?**

   No. El original permanece intacto en `data/raw`; el tablero consume una exportación analítica del dataset procesado.

4. **¿Por qué Power BI tiene una sola tabla?**

   Para simplificar la portabilidad y la exposición. Es una tabla analítica desnormalizada que ya contiene las variables necesarias y no requiere relaciones internas.

5. **¿Entonces se eliminó el modelo estrella?**

   No. El Data Mart estrella se conserva y se puede demostrar en SQL Server y SQLite. Únicamente se decidió no incluirlo dentro de Power BI.

6. **¿Qué hacen los segmentadores?**

   Cambian el contexto de filtro y hacen que las medidas DAX y las gráficas se recalculen para la selección actual.

7. **¿Qué diferencia hay entre redondez y compacidad?**

   La redondez mide la semejanza con un círculo; la compacidad relaciona el área con el eje mayor y resume qué tan concentrada es la figura.

8. **¿Por qué se usa el área promedio?**

   Permite comparar el tamaño típico de los granos entre variedades sin depender de un solo registro.

9. **¿Power BI ejecuta el modelo de clasificación?**

   No en este tablero. Power BI comunica y explora los datos; los modelos supervisados se entrenan y evalúan en Python con partición 70/30.

10. **¿Cómo se garantiza la reproducibilidad?**

    El repositorio incluye el CSV fuente, medidas DAX, tema, plantilla PBIT, proyecto versionable y el script que genera la estructura del tablero.

## Qué debes entender antes de la revisión

- Un **indicador** resume muchos registros en un solo valor.
- Una **medida DAX** se calcula según los filtros activos; no es una columna almacenada fila por fila.
- Un **segmentador** controla el contexto de filtro.
- Una visualización permite comparar; no demuestra causalidad.
- Los filtros del dashboard no cambian el CSV original.
- El 70/30 corresponde al entrenamiento y prueba de Machine Learning, no a la construcción del dashboard.
- La regresión predice una cantidad numérica, como `Area`; la clasificación predice una clase, como la variedad.

## Comprobación rápida antes de presentar

- El PBIX abre sin errores.
- Se observan dos páginas.
- Aparece una sola tabla: `DryBean_Analitica`.
- No existen relaciones ni modelo estrella dentro de Power BI.
- Las tarjetas muestran 13,543 registros y siete variedades sin filtros.
- Los tres segmentadores actualizan tarjetas y gráficas.
- El repositorio de GitHub está actualizado.
