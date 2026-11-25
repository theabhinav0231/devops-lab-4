#!/usr/bin/env bash
# Declarative GitOps reconciliation controller (single source of truth: Git HEAD)
set -euo pipefail
REPO_DIR="/home/abhinav/devops-lab-4"
NS="lab4-abhinav"
MANIFEST_DIR="${REPO_DIR}/gitops/manifests"

cd "$REPO_DIR"
GIT_SHA=$(git rev-parse --short HEAD)
DESIRED_REPLICAS=$(grep -E '^\s*replicas:' "$MANIFEST_DIR/deployment.yaml" | awk '{print $2}')
LIVE_REPLICAS=$(kubectl get deploy gitops-app -n "$NS" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

echo "[gitops] commit=${GIT_SHA} desired_replicas=${DESIRED_REPLICAS} live_replicas=${LIVE_REPLICAS}"
if ! kubectl diff -f "$MANIFEST_DIR" -n "$NS" >/dev/null 2>&1; then
  echo "[gitops] DRIFT OR UPDATE DETECTED -> reconciling cluster state to Git HEAD (${GIT_SHA})"
  kubectl apply -f "$MANIFEST_DIR" -n "$NS"
  kubectl rollout status deploy/gitops-app -n "$NS" --timeout=60s
else
  echo "[gitops] IN-SYNC: live cluster matches Git HEAD (${GIT_SHA})"
fi
