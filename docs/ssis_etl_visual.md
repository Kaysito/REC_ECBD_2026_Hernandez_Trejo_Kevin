# ETL visual en SQL Server Integration Services

## Proposito

El paquete `Package.dtsx` implementa visualmente la carga del Data Mart estrella de Dry Bean. Utiliza SQL Server Integration Services Projects en Visual Studio y la base local `DryBean_DataMart`.

## Flujo de control

1. **01 - EXTRACT - CSV a staging:** crea las tablas temporales y carga `data/processed/dry_beans_cleaned.csv` mediante `BULK INSERT`.
2. **02 - TRANSFORM - Limpiar y categorizar:** normaliza `Class` y deriva las categorías de tamaño y forma.
3. **03A - DIMENSION - DimVariedad:** comprueba que las siete clases de staging tengan una clave en `dim_variedad`.
4. **03B - DIMENSION - DimTamano:** comprueba las cuatro categorías de tamaño contra `dim_tamano`.
5. **03C - DIMENSION - DimForma:** comprueba las cuatro categorías de forma contra `dim_forma`.
6. **04 - HECHOS - FactBeanMorphology:** recibe las tres dimensiones, asigna sus claves y carga los 13,543 hechos.
7. **05 - VALIDATE - Integridad y conteos:** comprueba hechos, claves y restricciones, y elimina las tablas temporales.

Las flechas verdes representan restricciones de precedencia por éxito. Después de la transformación, las tres comprobaciones dimensionales se ejecutan en paralelo y convergen en la tabla de hechos. Esta distribución muestra visualmente la forma de estrella del Data Mart.

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
4. Confirmar que las siete tareas queden verdes y aparezca el mensaje: “La ejecución del paquete se completó correctamente”.

## Validacion realizada

La ejecución del 16 de noviembre de 2026 terminó correctamente. La comprobación posterior en SQL Server produjo:

- 13,543 filas en `fact_bean_morphology`;
- 13,543 identificadores `id_grano` únicos;
- 0 claves dimensionales inválidas;
- 0 incumplimientos reportados por `DBCC CHECKCONSTRAINTS`.

El proceso es repetible: la carga vacía la tabla de hechos antes de volver a insertar los registros y limpia las tablas de staging al finalizar.
