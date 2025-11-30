# MLOps GPU Resource Management Platform  
### Interactive Development + Production Training on Kubernetes

Bu proje, MLOps Engineer Case Study kapsamında tasarlanmış uçtan uca bir platformdur.  
Amaç, **GPU kaynaklarını verimli yöneten**, aynı kod tabanıyla hem  
**interactive development** hem **production-level training** yapılabilen bir  
**scalable ML platformu** oluşturmaktır.

Platform, HuggingFace tabanlı bir fine-tuning pipeline içerir ve aşağıdaki özellikleri sağlar:

---

# 🚀 Özellikler

### **🧪 Interactive Development**
- JupyterLab + Docker + GPU
- Küçük dataset ile hızlı deneme/yanılma
- `config/dev.yaml` ortamı

### **🏭 Production Training**
- Kubernetes üzerinde GPU Job scheduling
- PriorityClass ile **prod > dev** önceliklendirmesi
- Büyük dataset (S3/MinIO) ile scalable eğitim
- `config/prod.yaml` ortamı

### **📦 Unified Code Base**
Aynı kod tabanı (`train.py`, `model.py`, `dataset.py`) hem dev hem prod ortamında değişiklik yapılmadan çalışır.

### **📊 MLflow Experiment Tracking**
- Parametreler
- Metrikler
- Artifact (model) kayıtları  
- Dev/prod karşılaştırması

### **🔍 Observability**
- Pod log’ları  
- GPU allocation  
- MLflow metrikleri

---

# 📁 Proje Yapısı
├── README.md
├── src/
│   ├── train.py
│   ├── dataset.py
│   ├── model.py
│   ├── utils/
│   │   ├── logging_utils.py
│   │   ├── data_utils.py
│   │   └── gpu_utils.py
│   └── notebooks/
│       └── dev_notebook.ipynb
├── config/
│   ├── dev.yaml
│   └── prod.yaml
├── docker/
│   ├── Dockerfile.dev
│   └── Dockerfile.train
├── k8s/
│   ├── gpu-job.yaml
│   ├── priority-classes.yaml
│   └── nvidia-device-plugin.yaml
├── examples/
│   ├── run_dev.sh
│   ├── submit_job.sh
└── docs/
├── architecture.md
├── technology_choices.md
├── setup_guide.md
└── demo_scenarios.md
---

# 🧱 Kurulum ve Çalıştırma

## 1️⃣ Development Ortamı (Jupyter + GPU)

### 1. Docker dev imajını build et:

```bash
docker build -f docker/Dockerfile.dev -t mlops-dev .