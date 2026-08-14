# emergency-rollback.ps1 — Rollback de emergencia de un deployment.
#
# Prefiere Kubernetes (rollout undo); si no hay kubeconfig/K8s, revierte el
# commit anterior en git como fallback. NUNCA reemplaza el runbook de
# disaster-recovery: ejecutar primero el runbook, este script es el ultimo
# recurso operativo.
#
# Usage:
#   .opencode/scripts/emergency-rollback.ps1 <namespace/deployment> [--git]

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Target,

    [Parameter(Position = 1)]
    [string]$Mode = "k8s",

    [switch]$Git
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Target)) {
    [Console]::Error.WriteLine("uso: emergency-rollback.ps1 <namespace/deployment> [--git]")
    exit 1
}

$useGit = $Git.IsPresent -or ($Mode -in @("git", "--git", "-git"))

if ($useGit -or (-not (Get-Command kubectl -ErrorAction SilentlyContinue))) {
    Write-Output "Rollback git: revirtiendo al commit anterior..."
    & git reset --hard HEAD~1
    exit 0
}

if ($Target.Contains('/')) {
    $NS = $Target.Substring(0, $Target.IndexOf('/'))
    $DEPLOY = $Target.Substring($Target.LastIndexOf('/') + 1)
} else {
    $NS = $Target
    $DEPLOY = $Target
}

$null = & kubectl get deployment $DEPLOY -n $NS 2>&1
if ($LASTEXITCODE -ne 0) {
    [Console]::Error.WriteLine("error: deployment $DEPLOY no encontrado en ns $NS")
    exit 1
}

& kubectl rollout undo "deployment/$DEPLOY" -n $NS
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& kubectl rollout status "deployment/$DEPLOY" -n $NS --timeout=180s
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
