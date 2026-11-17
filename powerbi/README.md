# Dashboard Power BI — Dry Bean

SQL Server sigue siendo la fuente oficial. La copia SQLite mantiene el mismo esquema estrella y sirve como respaldo portátil. Para evitar depender de un controlador ODBC adicional, `data/bi/drybean_powerbi.csv` contiene una vista desnormalizada lista para una demostración rápida.

## Modelo recomendado

- Hechos: `fact_bean_morphology` (13,543 filas).
- Dimensiones: `dim_variedad` (7), `dim_tamano` (4) y `dim_forma` (4).
- Relaciones: uno a muchos, filtro unidireccional desde cada dimensión hacia hechos.

## Página 1 — Resumen ejecutivo

- Tarjetas: Total Granos, Variedades Analizadas, Área Promedio, Redondez Promedio y Compacidad Promedio.
- Segmentadores: variedad, categoría de tamaño y categoría de forma.
- Barras: total de granos por variedad.
- Matriz o mapa de calor: tamaño por forma.
- Dispersión: área contra perímetro, color por variedad.

## Página 2 — Morfología

- Box plot o columnas de área promedio por variedad.
- Barras de redondez y compacidad promedio.
- Tabla detallada con variedad, tamaño, forma y medidas principales.

## Recursos

- `medidas_dax.txt`: medidas listas para copiar.
- `tema_drybean.json`: colores y estilos del proyecto.
- `data/bi/drybean_powerbi.csv`: vista lista para importar.
- `data/datamart/drybean_datamart.sqlite`: copia portátil del esquema estrella.

En Power BI Desktop se recomienda **Obtener datos > SQL Server** y conectarse a `(localdb)\MSSQLLocalDB`, base `DryBean_DataMart`. Si el equipo de exposición no reconoce LocalDB, importar el CSV de respaldo.
