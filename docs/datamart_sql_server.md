# Data Mart Dry Bean en SQL Server

## Arquitectura dimensional

El proyecto utiliza un esquema estrella en la base `DryBean_DataMart`:

- `fact_bean_morphology`: 13,543 mediciones individuales de frijoles.
- `dim_variedad`: 7 variedades botánicas.
- `dim_tamano`: 4 categorías de tamaño.
- `dim_forma`: 4 categorías morfológicas.

Cada hecho contiene las 16 mediciones numéricas y tres claves foráneas hacia las dimensiones. El nivel de detalle o granularidad es **un registro por grano de frijol**.

## Instancia utilizada

- Motor: Microsoft SQL Server 2025 LocalDB Express, 64 bits.
- Instancia: `(localdb)\MSSQLLocalDB`.
- Autenticación: Windows.

## Ejecución reproducible

Desde la raíz del repositorio:

```powershell
$sqlcmd = 'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE'
$server = '(localdb)\MSSQLLocalDB'
$dataFile = (Resolve-Path 'data\processed\dry_beans_cleaned.csv').Path

& $sqlcmd -S $server -E -b -i 'sql\schema_datamart.sql'
& $sqlcmd -S $server -E -b -v ('DataFile="{0}"' -f $dataFile) -i 'sql\load_datamart.sql'
& $sqlcmd -S $server -E -b -i 'sql\validate_datamart.sql'
```

La carga es idempotente: antes de insertar vuelve a vaciar la tabla de hechos, por lo que ejecutarla otra vez no genera duplicados.

## Evidencia de validación

Validación ejecutada el 16 de noviembre de 2026:

| Tabla | Registros |
|---|---:|
| `dim_variedad` | 7 |
| `dim_tamano` | 4 |
| `dim_forma` | 4 |
| `fact_bean_morphology` | 13,543 |

- Identificadores de grano únicos: 13,543.
- Claves dimensionales inválidas: 0.
- Infracciones de claves foráneas detectadas por `DBCC CHECKCONSTRAINTS`: 0.
- Las dos vistas analíticas devuelven resultados por variedad y categoría de tamaño.

## Explicación breve para revisión

La tabla de hechos almacena las mediciones cuantitativas. Las dimensiones permiten analizar esas mediciones por variedad, tamaño y forma. Este modelo reduce la complejidad de las consultas analíticas y facilita su conexión con herramientas de visualización.
