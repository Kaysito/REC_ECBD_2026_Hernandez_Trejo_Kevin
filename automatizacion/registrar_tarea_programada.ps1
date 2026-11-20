param(
    [string]$TaskName = "ECBD_DryBean_ETL_0300"
)

$ErrorActionPreference = "Stop"
$runner = Join-Path $PSScriptRoot "ejecutar_etl_ssis.ps1"
$projectRoot = Split-Path -Parent $PSScriptRoot
$xmlPath = Join-Path $PSScriptRoot "$TaskName.xml"

if (-not (Test-Path -LiteralPath $runner)) {
    throw "No se encontro el ejecutor: $runner"
}

$arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$runner`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Actualiza diariamente el Data Mart Dry Bean mediante el paquete SSIS del proyecto ECBD." -Force | Out-Null
Export-ScheduledTask -TaskName $TaskName | Set-Content -LiteralPath $xmlPath -Encoding UTF8

$task = Get-ScheduledTask -TaskName $TaskName
$info = Get-ScheduledTaskInfo -TaskName $TaskName

[pscustomobject]@{
    Nombre = $task.TaskName
    Estado = $task.State
    ProximaEjecucion = $info.NextRunTime
    UltimaEjecucion = $info.LastRunTime
    UltimoResultado = $info.LastTaskResult
    EvidenciaXML = $xmlPath
}

