#!/usr/bin/env bash

# Basit güvenlik: hata olursa script'i durdur
set -euo pipefail

# Varsayılan image adı (Dockerfile.dev ile build ettiğin)
IMAGE_NAME="${IMAGE_NAME:-mlops-dev}"

# Proje root dizini (bu script examples/ altında duruyor, root = bir üst klasör)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==============================================="
echo "  MLOps Dev Environment - Jupyter + GPU"
echo "==============================================="
echo
echo "Project root      : ${PROJECT_ROOT}"
echo "Docker image      : ${IMAGE_NAME}"
echo
echo "Not:"
echo " - Bu script, JupyterLab'i 0.0.0.0:8888 üzerinde açar."
echo " - Host makinedeki proje klasörünü /workspace'e mount eder."
echo " - GPU'ya erişmek için --gpus all kullanır."
echo

# Docker image yoksa kullanıcıya küçük bir hatırlatma
if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
  echo "⚠️  Docker image '${IMAGE_NAME}' bulunamadı."
  echo "Önce şu komutu çalıştır:"
  echo
  echo "  docker build -f docker/Dockerfile.dev -t ${IMAGE_NAME} ."
  echo
  exit 1
fi

# Jupyter config için port
JUPYTER_PORT="${JUPYTER_PORT:-8888}"

# Container adı (isteğe bağlı güzellik)
CONTAINER_NAME="${CONTAINER_NAME:-mlops-dev-container}"

echo "JupyterLab'i başlatıyorum..."
echo "URL: http://localhost:${JUPYTER_PORT}"
echo

docker run --gpus all --rm \
  -p "${JUPYTER_PORT}:8888" \
  -v "${PROJECT_ROOT}:/workspace" \
  --name "${CONTAINER_NAME}" \
  -w /workspace \
  "${IMAGE_NAME}"