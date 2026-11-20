param(
    [string]$DtexecPath = "C:\Program Files\Microsoft SQL Server\130\DTS\Binn\DTExec.exe"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$packagePath = Join-Path $projectRoot "ssis\DryBean_ETL_SSIS\Package.dtsx"
$logDirectory = Join-Path $projectRoot "automatizacion\logs"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $logDirectory "etl_ssis_$timestamp.log"

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

function Write-Log {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    $line | Tee-Object -FilePath $logPath -Append
}

try {
    Write-Log "Inicio de la actualizacion automatica del Data Mart Dry Bean."

    if (-not (Test-Path -LiteralPath $DtexecPath)) {
        throw "No se encontro DTExec en: $DtexecPath"
    }
    if (-not (Test-Path -LiteralPath $packagePath)) {
        throw "No se encontro el paquete SSIS en: $packagePath"
    }

    Write-Log "Ejecutor SSIS: $DtexecPath"
    Write-Log "Paquete: $packagePath"
    Write-Log "Ejecutando el paquete creado en Visual Studio: EXTRACT, TRANSFORM, dimensiones, hechos y validacion."

    & $DtexecPath /File $packagePath /Reporting E 2>&1 |
        Tee-Object -FilePath $logPath -Append
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "DTExec termino con codigo $exitCode."
    }

    Write-Log "ETL finalizado correctamente. Data Mart actualizado y validado."
    exit 0
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

