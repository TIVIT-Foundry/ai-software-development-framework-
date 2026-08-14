# drift-detect.ps1 — Detect Terraform configuration drift.
#
# Runs `terraform plan -detailed-exitcode` (and refresh first, so the plan is
# based on current state). Exit codes:
#   0 = sin drift
#   1 = error
#   2 = drift detectado (plan no vacio)
#
# Usage:
#   cd <terraform-dir> && .opencode/scripts/drift-detect.ps1 [plan-options...]
#   .opencode/scripts/drift-detect.ps1 -TfDir <terraform-dir> [plan-options...]

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$TfDir = ".",

    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$PlanOptions = @()
)

$ErrorActionPreference = "Stop"

if ($TfDir -and $TfDir -ne ".") {
    Set-Location -Path $TfDir
}

if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine("error: terraform no instalado")
    exit 1
}

& terraform init -input=false -backend=false | Out-Null
if ($LASTEXITCODE -ne 0) {
    [Console]::Error.WriteLine("ERROR: terraform init fallo (exit $LASTEXITCODE)")
    exit $LASTEXITCODE
}

& terraform refresh -input=false | Out-Null
if ($LASTEXITCODE -ne 0) {
    [Console]::Error.WriteLine("ERROR: terraform refresh fallo (exit $LASTEXITCODE)")
    exit $LASTEXITCODE
}

$planArgs = @('plan', '-input=false', '-detailed-exitcode', '-out=drift.tfplan')
if ($PlanOptions -and $PlanOptions.Count -gt 0) {
    $planArgs += $PlanOptions
}

& terraform @planArgs
$code = $LASTEXITCODE

switch ($code) {
    0 { Write-Output "OK: sin drift" }
    2 { [Console]::Error.WriteLine("DRIFT: plan no vacio — revisar drift.tfplan") }
    Default { [Console]::Error.WriteLine("ERROR: terraform plan fallo (exit $code)") }
}

exit $code
