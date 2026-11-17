# ETL visual en SQL Server Integration Services

## Proposito

El paquete `Package.dtsx` implementa visualmente la carga del Data Mart estrella de Dry Bean. Utiliza SQL Server Integration Services Projects en Visual Studio y la base local `DryBean_DataMart`.

## Flujo de control

1. **01 - EXTRACT - CSV a staging:** crea las tablas temporales y carga `data/processed/dry_beans_cleaned.csv` mediante `BULK INSERT`.
2. **02 - TRANSFORM - Limpiar y categorizar:** normaliza `Class` y deriva las categorías de tamaño y forma.
3. **03 - LOAD - Cargar esquema estrella:** relaciona las dimensiones `dim_variedad`, `dim_tamano` y `dim_forma`, y carga `fact_bean_morphology`.
4. **04 - VALIDATE - Integridad y conteos:** exige 13,543 hechos, comprueba claves y restricciones, y elimina las tablas temporales.

Las flechas verdes representan restricciones de precedencia por éxito. Una etapa solo comienza cuando la anterior finaliza correctamente.

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
4. Confirmar que las cuatro tareas queden verdes y aparezca el mensaje: “La ejecución del paquete se completó correctamente”.

## Validacion realizada

La ejecución del 16 de noviembre de 2026 terminó correctamente. La comprobación posterior en SQL Server produjo:

- 13,543 filas en `fact_bean_morphology`;
- 13,543 identificadores `id_grano` únicos;
- 0 claves dimensionales inválidas;
- 0 incumplimientos reportados por `DBCC CHECKCONSTRAINTS`.

El proceso es repetible: la carga vacía la tabla de hechos antes de volver a insertar los registros y limpia las tablas de staging al finalizar.
