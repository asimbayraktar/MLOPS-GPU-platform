#!/usr/bin/env bash

# Hata olursa script'i durdur, unset değişkenleri hata say, pipe'da error'u taşı
set -euo pipefail

# Kullanım mesajı
usage() {
  cat <<EOF
Usage: $0 [prod|dev|both]

  prod  : Production GPU training job (mlops-train-prod)
  dev   : Dev GPU training job (mlops-train-dev)
  both  : Her iki job'ı da oluştur (priorityClass farkı ile GPU paylaşımını göstermek için)

Optional env vars:
  NAMESPACE   : K8s namespace (default: default)
  K8S_DIR     : K8s manifest klasörü (default: k8s)

Examples:
  $0 prod
  NAMESPACE=mlops $0 dev
  NAMESPACE=mlops K8S_DIR=deploy/k8s $0 both
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

MODE="$1"  # prod / dev / both

if [[ "${MODE}" != "prod" && "${MODE}" != "dev" && "${MODE}" != "both" ]]; then
  echo "❌ Invalid mode: ${MODE}"
  usage
  exit 1
fi

# Namespace ve k8s dizini
NAMESPACE="${NAMESPACE:-default}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K8S_DIR="${K8S_DIR:-${PROJECT_ROOT}/k8s}"

PRIORITY_FILE="${K8S_DIR}/priority-classes.yaml"
GPU_JOB_FILE="${K8S_DIR}/gpu-job.yaml"

echo "==============================================="
echo "   MLOps - K8s GPU Job Submitter"
echo "==============================================="
echo "Mode          : ${MODE}"
echo "Namespace     : ${NAMESPACE}"
echo "K8s dir       : ${K8S_DIR}"
echo

# kubectl var mı?
if ! command -v kubectl >/dev/null 2>&1; then
  echo "❌ 'kubectl' komutu bulunamadı. Lütfen kubectl kurulu ve PATH'te olduğundan emin ol."
  exit 1
fi

# Manifest dosyaları var mı?
if [[ ! -f "${PRIORITY_FILE}" ]]; then
  echo "❌ Priority classes file not found: ${PRIORITY_FILE}"
  exit 1
fi

if [[ ! -f "${GPU_JOB_FILE}" ]]; then
  echo "❌ GPU job file not found: ${GPU_JOB_FILE}"
  exit 1
fi

echo "➜ PriorityClass manifest apply ediliyor..."
kubectl apply -f "${PRIORITY_FILE}"

echo "➜ GPU Job manifest apply ediliyor..."
kubectl apply -f "${GPU_JOB_FILE}" -n "${NAMESPACE}"

# Job isimleri, gpu-job.yaml'daki ile aynı olmalı
PROD_JOB_NAME="mlops-train-prod"
DEV_JOB_NAME="mlops-train-dev"

# İlgili job'ı yeniden tetiklemek için eski job'ı siliyoruz
restart_job() {
  local job_name="$1"
  echo "➜ Eski job (varsa) siliniyor: ${job_name}"
  kubectl delete job "${job_name}" -n "${NAMESPACE}" --ignore-not-found

  echo "➜ Job yeniden oluşturuluyor: ${job_name}"
  # gpu-job.yaml içinde ilgili job tanımlı olduğundan apply yeterli
  kubectl apply -f "${GPU_JOB_FILE}" -n "${NAMESPACE}"

  echo "➜ Job durumu:"
  kubectl get job "${job_name}" -n "${NAMESPACE}"
}

case "${MODE}" in
  prod)
    # Sadece prod job'ı yeniden tetikle
    restart_job "${PROD_JOB_NAME}"
    ;;

  dev)
    # Sadece dev job'ı yeniden tetikle
    restart_job "${DEV_JOB_NAME}"
    ;;

  both)
    # Hem prod hem dev job'ı yeniden tetikle
    restart_job "${PROD_JOB_NAME}"
    restart_job "${DEV_JOB_NAME}"
    ;;
esac

echo
echo "✅ İşlem tamam. Logları izlemek için örnek komutlar:"
echo
if [[ "${MODE}" == "prod" || "${MODE}" == "both" ]]; then
  echo "  kubectl logs -n ${NAMESPACE} job/${PROD_JOB_NAME} -f"
fi
if [[ "${MODE}" == "dev" || "${MODE}" == "both" ]]; then
  echo "  kubectl logs -n ${NAMESPACE} job/${DEV_JOB_NAME} -f"
fi
echo