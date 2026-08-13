#!/usr/bin/env bash
# emergency-rollback.sh — Rollback de emergencia de un deployment.
#
# Prefiere Kubernetes (rollout undo); si no hay kubeconfig/K8s, revierte el
# commit anterior en git como fallback. NUNCA reemplaza el runbook de
# disaster-recovery: ejecutar primero el runbook, este script es el ultimo
# recurso operativo.
#
# Usage:
#   .opencode/scripts/emergency-rollback.sh <namespace/deployment> [--git]
set -euo pipefail

TARGET="${1:?uso: emergency-rollback.sh <namespace/deployment> [--git]}"
MODE="${2:-k8s}"

if [[ "$MODE" == "git" ]] || ! command -v kubectl >/dev/null 2>&1; then
  echo "Rollback git: revirtiendo al commit anterior..."
  git reset --hard HEAD~1
  exit 0
fi

NS="${TARGET%%/*}"
DEPLOY="${TARGET##*/}"

if ! kubectl get deployment "$DEPLOY" -n "$NS" >/dev/null 2>&1; then
  echo "error: deployment $DEPLOY no encontrado en ns $NS" >&2
  exit 1
fi

kubectl rollout undo "deployment/$DEPLOY" -n "$NS"
kubectl rollout status "deployment/$DEPLOY" -n "$NS" --timeout=180s
