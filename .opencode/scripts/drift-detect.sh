#!/usr/bin/env bash
# drift-detect.sh — Detect Terraform configuration drift.
#
# Runs `terraform plan -detailed-exitcode` (and refresh first, so the plan is
# based on current state). Exit codes:
#   0 = sin drift
#   1 = error
#   2 = drift detectado (plan no vacio)
#
# Usage:
#   cd <terraform-dir> && .opencode/scripts/drift-detect.sh [plan-options...]
set -euo pipefail

TF_DIR="${1:-.}"
shift || true

cd "$TF_DIR"

if ! command -v terraform >/dev/null 2>&1; then
  echo "error: terraform no instalado" >&2
  exit 1
fi

terraform init -input=false -backend=false >/dev/null
terraform refresh -input=false >/dev/null

set +e
terraform plan -input=false -detailed-exitcode -out=drift.tfplan "$@"
code=$?
set -e

case "$code" in
  0) echo "OK: sin drift";;
  2) echo "DRIFT: plan no vacio — revisar drift.tfplan" >&2;;
  *) echo "ERROR: terraform plan fallo (exit $code)" >&2;;
esac
exit "$code"
