[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$DeviceId,

    [Parameter(Mandatory)]
    [string]$TraitIds,

    [Parameter(Mandatory)]
    [DateTimeOffset]$StartLocal,

    [Parameter(Mandatory)]
    [DateTimeOffset]$EndLocal,

    [string]$OutputPath,

    [switch]$SkipDiscovery
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($EndLocal -le $StartLocal) {
    throw 'EndLocal must be later than StartLocal.'
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $projectRoot)
$registryPath = Join-Path $projectRoot 'config\brightlayer-test-devices.json'
$probePath = Join-Path $PSScriptRoot 'probe_brightlayer_device.py'
$pythonPath = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
$registry = Get-Content $registryPath -Raw | ConvertFrom-Json
$secureSecret = Read-Host 'Brightlayer service account secret' -AsSecureString
$secretPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureSecret)

try {
    $env:BRIGHTLAYER_SERVICE_ACCOUNT_ID = $registry.serviceAccountId
    $env:BRIGHTLAYER_SERVICE_ACCOUNT_SECRET = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPointer)
    $env:BRIGHTLAYER_PROBE_DEVICE_ID = $DeviceId
    $env:BRIGHTLAYER_PROBE_TRAIT_IDS = $TraitIds
    $env:BRIGHTLAYER_PROBE_START_UTC = $StartLocal.UtcDateTime.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $env:BRIGHTLAYER_PROBE_END_UTC = $EndLocal.UtcDateTime.ToString('yyyy-MM-ddTHH:mm:ssZ')

    if ($SkipDiscovery) {
        $env:BRIGHTLAYER_PROBE_QUICK = '1'
    }

    if ($OutputPath) {
        $directory = Split-Path -Parent $OutputPath
        if ($directory) {
            New-Item -ItemType Directory -Force $directory | Out-Null
        }
        & $pythonPath $probePath | Tee-Object -FilePath $OutputPath
    }
    else {
        & $pythonPath $probePath
    }
}
finally {
    if ($secretPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPointer)
    }
    Remove-Item Env:BRIGHTLAYER_SERVICE_ACCOUNT_ID, Env:BRIGHTLAYER_SERVICE_ACCOUNT_SECRET, Env:BRIGHTLAYER_PROBE_DEVICE_ID, Env:BRIGHTLAYER_PROBE_TRAIT_IDS, Env:BRIGHTLAYER_PROBE_START_UTC, Env:BRIGHTLAYER_PROBE_END_UTC, Env:BRIGHTLAYER_PROBE_QUICK -ErrorAction SilentlyContinue
    $secureSecret = $null
}