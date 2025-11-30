# Setup & Deployment Guide  
*MLOps GPU Resource Management Platform*

Bu doküman, platformun **sıfırdan kurulumu**, **development ortamının açılması**,  
**production ortamında GPU training job’larının çalıştırılması**,  
**MLflow ve MinIO entegrasyonu**,  
ve tüm pipeline’ın uçtan uca görüntülenmesi için gerekli olan tüm adımları içerir.

---

# 1. Sistem Gereksinimleri

### Minimum:
- Docker (GPU destekli)
- NVIDIA GPU (RTX / Tesla / A40 / A100 / V100 vb.)
- NVIDIA Driver (>= 470.x)
- Docker için NVIDIA Container Toolkit:  
  https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

### Production Mode İçin Ekstralar:
- Kubernetes cluster (minikube, kind, microk8s, GKE, EKS, OpenShift vs.)
- NVIDIA GPU Device Plugin  
- kubectl

---

# 2. Proje Yapısının Klonlanması

```bash
git clone <repo-url> mlops-gpu-platform
cd mlops-gpu-platform