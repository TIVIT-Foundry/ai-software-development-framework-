# setup-venv.ps1 — Create the venv for validators.
# Idempotent: re-running on an existing venv is a no-op.
#
# Usage:
#   .opencode\validators\setup-venv.ps1
#
# After this, run the validators with:
#   .opencode\validators\run-all.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ValidatorsDir = Join-Path (Split-Path -Parent $ScriptDir) "validators"
$VenvDir = Join-Path $ValidatorsDir ".venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPy)) {
    Write-Host "Creating venv at $VenvDir ..."
    python -m venv $VenvDir
} else {
    Write-Host "Venv already exists at $VenvDir"
}

Write-Host ""
Write-Host "Done. Validator runner: powershell -File $(Join-Path $ScriptDir 'run-all.ps1')"
