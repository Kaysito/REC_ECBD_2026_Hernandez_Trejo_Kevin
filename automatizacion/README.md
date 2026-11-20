# Automatización del ETL SSIS

La tarea de Windows `ECBD_DryBean_ETL_0300` ejecuta diariamente el paquete `ssis/DryBean_ETL_SSIS/Package.dtsx` a las 03:00.

## Funcionamiento

1. El Programador de tareas inicia `automatizacion/ejecutar_etl_ssis.ps1`.
2. El script utiliza el runtime `DTExec` de SQL Server instalado en el equipo para ejecutar el paquete creado y mantenido en Visual Studio Community.
3. El paquete carga el CSV procesado en staging, transforma categorías, comprueba las dimensiones, carga `FactBeanMorphology` y valida 13,543 hechos.
4. Cada ejecución genera un archivo en `automatizacion/logs/` con fecha, salida y resultado.
5. La opción `StartWhenAvailable` permite recuperar una ejecución omitida cuando el equipo vuelve a estar disponible.

La tarea se registra para el usuario actual y se ejecuta únicamente en su sesión. La computadora debe estar encendida y el usuario debe mantener una sesión iniciada. Visual Studio no necesita permanecer abierto.

## Registrar o actualizar la tarea

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File automatizacion\registrar_tarea_programada.ps1
```

## Ejecutar una prueba manual

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File automatizacion\ejecutar_etl_ssis.ps1
```

## Evidencias

- `ECBD_DryBean_ETL_0300.xml`: configuración exportada del Programador de tareas.
- `logs/`: bitácoras de ejecución con código de salida y mensajes de validación.
- `Package.dtsx`: flujo visual de extracción, transformación, dimensiones, hechos y validación.

