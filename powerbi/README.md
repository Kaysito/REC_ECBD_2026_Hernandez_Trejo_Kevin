# Dashboard Power BI — Dry Bean

El archivo final usa **una sola tabla analítica** denominada `DryBean_Analitica`. No se agregó un modelo estrella ni relaciones dentro de Power BI, tal como se decidió para simplificar la exposición. La tabla proviene de `data/bi/drybean_powerbi.csv` y contiene 13,543 registros limpios.

El modelo estrella se conserva, por separado, en SQL Server y SQLite como evidencia de Data Mart. Power BI no depende de esas relaciones para abrir ni para utilizar sus filtros.

## Archivos de entrega

- `Hernandez_Trejo_Kevin_Dashboard_DryBean.pbix`: tablero terminado y con datos cargados.
- `Hernandez_Trejo_Kevin_Dashboard_DryBean.pbit`: plantilla reproducible del tablero.
- `DryBean_Dashboard_PbixProj/`: fuentes versionables del informe.
- `generar_dashboard_pbit.py`: generador reproducible de la plantilla.

## Página 1 — Resumen ejecutivo

- Tarjetas: Total Granos, Variedades Analizadas, Área Promedio, Redondez Promedio y Compacidad Promedio.
- Segmentadores: variedad, categoría de tamaño y categoría de forma.
- Barras: total de granos por variedad.
- Tabla detallada de indicadores por variedad.

## Página 2 — Morfología

- Tarjetas de área mínima, área máxima, perímetro y solidez promedio.
- Distribución por categoría de tamaño y categoría de forma.
- Comparación de redondez y compacidad por variedad.
- Tabla detallada con variedad y medidas morfológicas.

## Recursos

- `medidas_dax.txt`: medidas listas para copiar.
- `tema_drybean.json`: colores y estilos del proyecto.
- `data/bi/drybean_powerbi.csv`: vista lista para importar.
- `data/datamart/drybean_datamart.sqlite`: copia portátil del esquema estrella, externa a Power BI.

Para la exposición basta con abrir el archivo `.pbix`. Si se mueve el repositorio y Power BI solicita actualizar la fuente, seleccione `data/bi/drybean_powerbi.csv` y pulse **Actualizar**.
