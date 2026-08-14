# check-phase-gate.ps1 — Enforce Artifact Gates before phase transitions (N0-N49)
#
# Verifies that required artifacts exist on disk before an agent or developer
# advances to downstream phases (Scaffold, Backend, Frontend, QA).
#
# Usage:
#   powershell -File .opencode/validators/check-phase-gate.ps1 [-TargetPhase <A|B|C|D|E|F|G|H|all>] [-Strict]

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'all')]
    [string]$TargetPhase = 'all',

    [switch]$Strict
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
Set-Location -Path $RootDir

$Gates = [ordered]@{
    'Phase A (Governance/Discovery)' = @{
        'Required' = @('docs/governance.md', 'docs/constitution.md')
        'Description' = 'Reglas de gobernanza y constitucion del proyecto'
    }
    'Phase B (Architecture)' = @{
        'Required' = @('docs/artifacts/discovery.md', 'docs/artifacts/conception.md')
        'Description' = 'Discovery del vertical y concepcion funcional'
    }
    'Phase C (Scaffold)' = @{
        'Required' = @('docs/artifacts/architecture.md', 'docs/artifacts/core.md')
        'Description' = 'Arquitectura tecnica y core agentico'
    }
    'Phase D (Specification)' = @{
        'Required' = @('docs/artifacts/pack.md')
        'Description' = 'Pack vertical como producto'
    }
    'Phase E (Backend Implementation)' = @{
        'RequiredDirs' = @('docs/api-first', 'docs/specs')
        'Description' = 'Especificacion API-first o Feature-spec aprobada'
    }
    'Phase F (Frontend Implementation)' = @{
        'RequiredDirs' = @('docs/api-first', 'docs/specs')
        'Description' = 'Especificacion de API/UI'
    }
    'Phase G (QA & Validation)' = @{
        'RequiredDirs' = @('src')
        'Description' = 'Codigo implementado en src/'
    }
    'Phase H (Operations & Release)' = @{
        'Required' = @('docs/artifacts/qa.md')
        'Description' = 'Evidencia de validacion y gate go/no-go'
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " TIVIT Foundry -- Artifact Gate Validator (Protocol v2.0)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$failedGates = 0
$passedGates = 0

foreach ($phaseName in $Gates.Keys) {
    $gate = $Gates[$phaseName]
    $phaseLetter = $phaseName.Substring(6, 1)

    if ($TargetPhase -ne 'all' -and $TargetPhase -ne $phaseLetter) {
        continue
    }

    $allPresent = $true
    $missingItems = @()

    if ($gate.ContainsKey('Required')) {
        foreach ($file in $gate['Required']) {
            if (-not (Test-Path $file)) {
                $allPresent = $false
                $missingItems += $file
            }
        }
    }

    if ($gate.ContainsKey('RequiredDirs')) {
        $hasAnySpec = $false
        foreach ($dir in $gate['RequiredDirs']) {
            if (Test-Path $dir) {
                $count = (Get-ChildItem -Path $dir -Filter "*.md" -Recurse | Where-Object { $_.Name -ne "README.md" } | Measure-Object).Count
                if ($count -gt 0) {
                    $hasAnySpec = $true
                    break
                }
                if ($dir -eq 'src') {
                    $codeCount = (Get-ChildItem -Path $dir -Recurse | Measure-Object).Count
                    if ($codeCount -gt 0) { $hasAnySpec = $true; break }
                }
            }
        }
        if (-not $hasAnySpec) {
            $allPresent = $false
            $missingItems += ("Archivos en: " + ($gate['RequiredDirs'] -join ' o '))
        }
    }

    if ($allPresent) {
        Write-Host "  [PASS] $phaseName" -ForegroundColor Green
        Write-Host "         $($gate['Description'])" -ForegroundColor DarkGray
        $passedGates++
    } else {
        Write-Host "  [GATE-OPEN] $phaseName" -ForegroundColor Yellow
        Write-Host "         $($gate['Description'])" -ForegroundColor DarkGray
        foreach ($m in $missingItems) {
            Write-Host "         - Faltante: $m" -ForegroundColor DarkYellow
        }
        $failedGates++
    }
    Write-Host ""
}

Write-Host "Resumen: $passedGates gates listos, $failedGates gates pendientes" -ForegroundColor White

if ($Strict.IsPresent -and ($failedGates -gt 0)) {
    Write-Host "Error: Fallaron gates requeridos en modo estricto." -ForegroundColor Red
    exit 1
}

exit 0
