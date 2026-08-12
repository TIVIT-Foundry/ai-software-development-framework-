# run-all.ps1 — Execute all framework validators and report.
# Exit code 0 only if all checks pass.
#
# Python selection:
#   - Prefers the venv at .opencode\validators\.venv\Scripts\python.exe
#   - Falls back to system python
#
# Setup the venv once with:
#   .opencode\validators\setup-venv.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Pick the right python interpreter
$VenvPy = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (Test-Path $VenvPy) {
    $Py = $VenvPy
} else {
    $Py = "python"
}

$total = 0
$passed = 0
$failed = 0

function Run-Check {
    param(
        [string]$Name,
        [string]$Script
    )
    $script:total++
    # Capture all output but decide success by the exit code, not by stderr
    # presence: a check that fails printing to stdout only must still FAIL,
    # and a check that warns to stderr while passing must still PASS.
    & $Py (Join-Path $ScriptDir $Script) *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK $Name" -ForegroundColor Green
        $script:passed++
    } else {
        Write-Host "  FAIL $Name (exit $LASTEXITCODE)" -ForegroundColor Red
        $script:failed++
    }
}

Write-Host "Using Python: $Py"
Write-Host ""

# Run each validator
Run-Check "check-dependencies"           "check-dependencies.py"
Run-Check "check-refs"                   "check-refs.py"
Run-Check "check-secrets"                "check-secrets.py"
Run-Check "check-skill-contract"         "check-skill-contract.py"
Run-Check "check-mcp-config"             "check-mcp-config.py"
Run-Check "check-content-quality"        "check-content-quality.py"
Run-Check "check-skill-ids"              "check-skill-ids.py"
Run-Check "check-duplicate-descriptions" "check-duplicate-descriptions.py"
Run-Check "check-orphan-skills"          "check-orphan-skills.py"
Run-Check "check-level-coverage"         "check-level-coverage.py"
Run-Check "check-consumed-by-cycles"     "check-consumed-by-cycles.py"
Run-Check "check-version-bumps"          "check-version-bumps.py"
Run-Check "check-bundle-consistency"     "check-bundle-consistency.py"
Run-Check "check-scaffold-stack"          "check-scaffold-stack.py"

Write-Host ""
Write-Host "$passed passed, $failed failed (total $total)"

if ($failed -gt 0) {
    exit 1
}
exit 0
