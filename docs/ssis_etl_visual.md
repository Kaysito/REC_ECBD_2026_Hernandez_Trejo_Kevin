# ETL visual en SQL Server Integration Services

## Proposito

El paquete `Package.dtsx` implementa visualmente la carga del Data Mart estrella de Dry Bean. Utiliza SQL Server Integration Services Projects en Visual Studio y la base local `DryBean_DataMart`.

## Flujo de control

1. **00 - PREPARE - Crear esquema full:** crea las tres dimensiones y la tabla de hechos si fueron eliminadas, crea índices y prepara una carga completa.
2. **01 - EXTRACT - CSV a staging:** crea las tablas temporales y carga `data/processed/dry_beans_cleaned.csv` mediante `BULK INSERT`.
3. **02 - TRANSFORM - Limpiar y categorizar:** normaliza `Class` y deriva las categorías de tamaño y forma.
4. **03A - DIMENSION - DimVariedad:** reinicia y carga el catálogo de siete variedades.
5. **03B - DIMENSION - DimTamano:** reinicia y carga el catálogo de cuatro categorías de tamaño.
6. **03C - DIMENSION - DimForma:** reinicia y carga el catálogo de cuatro categorías de forma.
7. **03D - DIMENSION - DimTiempo:** registra la fecha de ejecución con clave `YYYYMMDD`, año, trimestre, mes y día.
8. **04 - HECHOS - FactBeanMorphology:** recibe las cuatro dimensiones, asigna sus claves y carga los 13,543 hechos.
9. **05 - VALIDATE - Integridad y conteos:** comprueba hechos, claves y restricciones, y elimina las tablas temporales.

Las flechas verdes representan restricciones de precedencia por éxito. Después de la transformación, las cuatro dimensiones se ejecutan en paralelo y convergen en la tabla de hechos. Esta distribución muestra visualmente la forma de estrella del Data Mart.

## Conexion

- Administrador: `CN_DryBean_DataMart`
- Servidor: `(localdb)\MSSQLLocalDB`
- Base: `DryBean_DataMart`
- Seguridad: autenticación integrada de Windows
- Proveedor: Microsoft OLE DB Driver 19 for SQL Server

## Ejecucion

1. Abrir `ssis/DryBean_ETL_SSIS/DryBean_ETL_SSIS.slnx`.
2. Abrir `Package.dtsx` y seleccionar **Flujo de control**.
3. Presionar **Iniciar** o `F5`.
4. Confirmar que las nueve tareas queden verdes y aparezca el mensaje: “La ejecución del paquete se completó correctamente”.

## Validacion realizada

La prueba de recuperación del 20 de noviembre de 2026 eliminó deliberadamente las cuatro tablas del Data Mart y ejecutó el paquete. El paquete reconstruyó el esquema y produjo:

- 13,543 filas en `fact_bean_morphology`;
- 13,543 identificadores `id_grano` únicos;
- 0 claves dimensionales inválidas;
- 0 incumplimientos reportados por `DBCC CHECKCONSTRAINTS`.

Una segunda ejecución consecutiva conservó exactamente 7 variedades, 4 tamaños, 4 formas y 13,543 hechos. Por tanto, es una carga completa repetible: reconstruye lo faltante, reinicia catálogos y hechos, y limpia staging al finalizar.
