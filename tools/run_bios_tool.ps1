$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "bios_tool.py"
$python = Get-Command python -ErrorAction SilentlyContinue

if ($python) {
    & $python.Source $scriptPath @args
    exit $LASTEXITCODE
}

$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    & $pyLauncher.Source -3 $scriptPath @args
    exit $LASTEXITCODE
}

$codexPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path $codexPython) {
    & $codexPython $scriptPath @args
    exit $LASTEXITCODE
}

Write-Error "No Python runtime found. Install Python 3 or run this from Codex with the bundled runtime available."
exit 1

