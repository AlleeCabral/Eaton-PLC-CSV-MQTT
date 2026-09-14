param(
    [string]$OutputPath = "artifacts/namibia-aggregation.zip",
    [string]$PythonPath = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceRoot = Join-Path $projectRoot "src"
$outputCandidate = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath
} else {
    Join-Path $projectRoot $OutputPath
}
$resolvedOutput = [System.IO.Path]::GetFullPath($outputCandidate)
$stageRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("namibia-function-" + [guid]::NewGuid())

try {
    New-Item -ItemType Directory -Path $stageRoot | Out-Null
    New-Item -ItemType Directory -Path (Split-Path $resolvedOutput) -Force | Out-Null

    foreach ($file in @("function_app.py", "host.json", "requirements.txt", "__init__.py")) {
        Copy-Item (Join-Path $sourceRoot $file) $stageRoot
    }
    Copy-Item (Join-Path $sourceRoot "modules") $stageRoot -Recurse
    Copy-Item (Join-Path $sourceRoot "shared") $stageRoot -Recurse

    Get-ChildItem $stageRoot -Recurse -Directory |
        Where-Object Name -eq "__pycache__" |
        Remove-Item -Recurse -Force
    Get-ChildItem $stageRoot -Recurse -File -Include "*.pyc" | Remove-Item -Force

    $packageTarget = Join-Path $stageRoot ".python_packages/lib/site-packages"
    & $PythonPath -m pip install `
        --requirement (Join-Path $sourceRoot "requirements.txt") `
        --target $packageTarget `
        --disable-pip-version-check `
        --no-compile
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed with exit code $LASTEXITCODE"
    }

    if (Test-Path $resolvedOutput) {
        Remove-Item $resolvedOutput -Force
    }
    Push-Location $stageRoot
    try {
        & tar.exe -a -c -f $resolvedOutput *
        if ($LASTEXITCODE -ne 0) {
            throw "Archive creation failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($resolvedOutput)
    try {
        $entries = @($archive.Entries | ForEach-Object FullName)
        $duplicates = @($entries | Group-Object | Where-Object Count -gt 1)
        $localArtifacts = @($entries | Where-Object {
            $_ -match "(^|/)(\.venv|__pycache__)(/|$)" -or
            $_ -match "^(tests|local\.settings|artifacts)(/|\.|$)" -or
            $_ -match "\.pyc$"
        })
        $missing = @("function_app.py", "host.json", "requirements.txt") |
            Where-Object { $_ -notin $entries }

        if ($duplicates.Count -gt 0) { throw "Archive contains duplicate entries" }
        if ($entries | Where-Object { $_ -match "\\" }) { throw "Archive contains Windows path separators" }
        if ($missing.Count -gt 0) { throw "Archive is missing root files: $($missing -join ', ')" }
        if ($localArtifacts.Count -gt 0) { throw "Archive contains local artifacts: $($localArtifacts -join ', ')" }
        if (-not ($entries | Where-Object { $_ -like ".python_packages/lib/site-packages/azure/functions/*" })) {
            throw "Archive does not contain installed Azure Functions dependencies"
        }
    }
    finally {
        $archive.Dispose()
    }

    Get-Item $resolvedOutput | Select-Object FullName, Length, LastWriteTimeUtc
}
finally {
    if (Test-Path $stageRoot) {
        Remove-Item $stageRoot -Recurse -Force
    }
}