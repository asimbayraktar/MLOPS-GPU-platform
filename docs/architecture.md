# MLOps GPU Resource Management Platform – Architecture Overview

## 1. Amaç

Bu platform, data scientist ve ML engineer ekibinin:

- **Interactive Development** (küçük veri + hızlı deneme)
- **Production Training** (büyük veri + GPU cluster)

ihtiyaçlarını **tek bir kod tabanı** üzerinden, GPU kaynaklarını verimli kullanarak karşılamak için tasarlanmıştır.

Aynı `train.py` kodu hem Jupyter ortamında hem de Kubernetes GPU job’ları içinde çalışır. Farklı ortamlar yalnızca **config dosyası** (dev/prod) ve **çalıştırma şekli** ile ayrılır.

---

## 2. High-Level Mimarisi

### 2.1. Bileşenler

1. **Interactive Dev Environment (Jupyter + Docker + GPU)**
   - Data scientist’ler için GPU destekli JupyterLab container’ı
   - Küçük dataset’lerle hızlı experiment ve debugging
   - `config/dev.yaml` ile çalışır

2. **Production Training Environment (Kubernetes GPU Cluster)**
   - Kubernetes üzerinde çalışan GPU Job’lar
   - `config/prod.yaml` ile büyük veri setlerinde eğitim
   - K8s `Job` + `PriorityClass` ile resource management

3. **Model Training Pipeline**
   - `src/train.py`: ana entrypoint
   - `src/dataset.py`: CSV tabanlı text classification dataset loader
   - `src/model.py`: HuggingFace `distilbert-base-uncased` fine-tuning
   - `src/utils/logging_utils.py`: MLflow entegrasyonu

4. **Data Layer**
   - **Dev**: Local klasör (`./data/sample-small`)
   - **Prod**: MinIO/S3 (`s3://datasets/large-dataset`)
   - S3 erişimi için `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` environment değişkenleri

5. **Experiment Tracking (MLflow)**
   - Tüm deney parametreleri, metrikler ve modeller MLflow’a loglanır
   - Dev: `http://localhost:5000`
   - Prod (K8s): `http://mlflow:5000`

6. **Artifact & Model Storage**
   - Dev: Local `./outputs/dev`
   - Prod: `s3://models/production`

7. **GPU Resource Management ve Scheduling**
   - NVIDIA GPU Operator / device plugin ile GPU’lar K8s’e tanıtılır
   - `PriorityClass` ile **prod işlerine yüksek öncelik**, **dev işlerine düşük öncelik**
   - Kısıtlı GPU ortamında prod job’lar öncelik alır, dev job’lar sırada bekler

8. **Monitoring & Observability (isteğe bağlı genişletme)**
   - Kubernetes metrikleri: CPU/GPU/Memory kullanımına Prometheus + Grafana ile bakılabilir
   - Eğitim seviyesi metrikler: MLflow üzerinde accuracy, loss, epoch bazlı log

---

## 3. Akış Diyagramı (Metinle Temsil)

```text
                +---------------------+
                |     Developer       |
                | (Data Scientist)    |
                +----------+----------+
                           |
                           | 1. Kod & notebook geliştirme
                           v
              +---------------------------+
              |  Docker Dev Container     |
              |  (Jupyter + GPU)          |
              +---------------------------+
                           |
      +--------------------+--------------------+
      |                                         |
  2a. Dev training                          2b. Kod stabil
      (config/dev.yaml)                        |
      |                                        v
      v                              +---------------------+
+-------------------+                |   Git Repository   |
|  Local Dataset    |                +---------+----------+
+---------+---------+                          |
          |                                     |
          v                                     | 3. CI/CD veya manuel build
+---------------------------+                   v
|  train.py / dev config    |          +----------------------+
|  MLflow (local)           |          | Train Docker Image   |
+---------------------------+          +----------+-----------+
                                                  |
                                                  | 4. Deploy to K8s
                                                  v
                                    +-------------------------------+
                                    |   Kubernetes GPU Cluster      |
                                    +-------------------------------+
                                      |          |
                                      |          |
                               5a. Prod Job  5b. Dev Job
                                   (high)        (low)
                                      |          |
                                      v          v
                          +----------------+   +----------------+
                          | train.py +     |   | train.py +     |
                          | config/prod    |   | config/dev     |
                          +--------+-------+   +--------+-------+
                                   |                    |
                                   v                    v
                             +-----------+        +-----------+
                             |  S3/MinIO |        | MLflow   |
                             +-----------+        +-----------+