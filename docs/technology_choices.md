# Technology Choices & Rationale

Bu doküman, MLOps GPU Training Platformunda kullanılan tüm teknolojilerin *neden seçildiğini*, *alternatiflerinin ne olduğunu* ve *trade-off’larını* açıklamaktadır.

---

# 1. Containerization & Environment

## **Docker**
**Neden seçildi?**
- Her ortamda aynı bağımlılıklarla çalışmayı sağlar
- GPU destekli PyTorch/TensorFlow imajları kolayca kullanılabilir
- Jupyter dev ortamı ve production training imajı aynı tabanda yönetilebilir

**Alternatifler**
- Podman (rootless, daha güvenli)
- Singularity (HPC ortamlarında popüler)

**Trade-off**
- Docker root yetkisi gerektirir → güvenlik açısından kısıtlı bazı kurumlarda Podman tercih edilir.

---

# 2. GPU Support Layer

## **NVIDIA CUDA + NVIDIA PyTorch Base Image**
**Neden seçildi?**
- CUDA + cuDNN tek imajda stabil bir şekilde gelir
- PyTorch GPU ile sorunsuz çalışır
- HuggingFace modellerinin %90’ı PyTorch tabanlıdır

**Alternatifler**
- TensorFlow base images
- Conda ile manuel CUDA kurulumu

**Trade-off**
- NVIDIA base imageleri büyük boyutludur (3–5GB)
- TensorFlow eğitimi istense farklı bir imaj gerekebilir

---

# 3. Orchestration & Scheduling

## **Kubernetes (K8s)**
**Neden seçildi?**
- GPU scheduling için endüstri standardıdır
- Çok kullanıcı + çok job ortamlarında en stabil çözüm
- PriorityClass ile *prod > dev* önceliklendirmesi yapılabilir
- Job retry, backoffLimit, TTL gibi güçlü mekanizmalar mevcut

**Alternatifler**
- Slurm (HPC merkezlerde çok kullanılır)
- Airflow (job schedule, ama GPU resource allocation yok)
- Kubeflow Pipelines (daha “ML-native” ama setup daha ağır)

**Trade-off**
- K8s kurulumu ve yönetimi daha karmaşıktır
- GPU node eklemek için cluster yönetimi gerekir

---

# 4. GPU Resource Plugin

## **NVIDIA Kubernetes Device Plugin / GPU Operator**
**Neden seçildi?**
- GPU’ları Kubernetes’e otomatik olarak node resource olarak tanıtır
- nvidia.com/gpu şeklinde limits/request kullanılmasını sağlar
- Cluster GPU sağlığını takip eder

**Alternatifler**
- AMD ROCm Device Plugin (AMD GPU ortamları için)
- Custom DaemonSet yazmak (önerilmez)

**Trade-off**
- Yalnızca NVIDIA GPU’larda çalışır

---

# 5. Model Training Framework

## **HuggingFace Transformers**
**Neden seçildi?**
- Pre-trained modellerin en büyük ekosistemi
- Fine-tuning API’si basit ve modüler
- Trainer API → distributed training medya destekli
- PyTorch backend ile GPU performansı güçlü

**Alternatifler**
- TensorFlow Keras
- PyTorch Lightning
- OpenAI Whisper / CLIP özel modelleri

**Trade-off**
- Çok büyük modellerde (LLaMA, Falcon gibi) GPU memory ihtiyacı yüksek olabilir
- Bazı modeller TF destekli olabilir ama PyTorch değil (nadir)

---

# 6. Experiment Tracking

## **MLflow**
**Neden seçildi?**
- Parametre, metrik ve model artifact yönetiminde endüstri standardı
- Hem lokal Jupyter dev ortamında hem Kubernetes prod ortamında aynı şekilde çalışır
- Hafif bir setup → docker-compose veya tek container ile kullanılabilir
- S3/MinIO backend storage ile production-ready

**Alternatifler**
- Weights & Biases (W&B) → En gelişmiş UI, fakat SaaS → maliyet
- Neptune.ai → Güçlü ama yine SaaS
- TensorBoard → görsel taraf güçlü fakat işlevsel olarak sınırlı

**Trade-off**
- MLflow UI W&B kadar modern değildir
- Çok büyük deney hacimlerinde MLflow scaling ayarları gerekebilir

---

# 7. Storage Layer

## **MinIO / S3**
**Neden seçildi?**
- Hem local hem production ortamda S3 protokolü ile çalışır
- MLflow backend olarak destekler
- Dataset & model artifact’lerinin versioned saklanmasına izin verir
- K8s üzerinde kolayca dağıtılabilir

**Alternatifler**
- Google Cloud Storage (GCS)
- AWS S3
- Azure Blob Storage
- Local FS (uygunsuz: ölçeklenemez)

**Trade-off**
- Local MinIO cluster = ek bakım
- AWS S3 çok daha stabil ama maliyetli

---

# 8. Monitoring & Observability

## **Prometheus + Grafana (Opsiyonel fakat önerilir)**
**Neden seçildi?**
- Kubernetes CPU/GPU metriklerini otomatik toplar
- Eğitim job’larının resource kullanımını izlemeyi sağlar
- Grafana dashboard’ları kolay kişiselleştirilir

**Alternatifler**
- Datadog (ücretli)
- New Relic
- OpenTelemetry stack

**Trade-off**
- Kurulum ek adımlar gerektirir
- Dashboard tasarımı zaman alır

---

# 9. Dataset Layer & Format

## **CSV + HuggingFace Datasets**
**Neden seçildi?**
- Eğitim için hızlı prototip ve kolay entegre edilebilir format
- Küçük dataset’lerde notebook ile pratik kullanım
- `datasets` modülü ile kolay loading, splitting ve caching

**Alternatifler**
- Parquet (büyük dataset’ler için ideal)
- TFRecord (TensorFlow pipeline’ları için)
- HuggingFace Dataset Hub (public dataset’ler için)

**Trade-off**
- Çok büyük dataset’lerde CSV ideal değildir (okuma yavaş)
- Parquet büyük ölçekte daha performanslıdır

---

# 10. Dev Environment

## **JupyterLab + Docker GPU Container**
**Neden seçildi?**
- Data scientist’ler için en rahat çalışma ortamı
- Yol bağımsız → host makinede environment conflict riskini ortadan kaldırır
- Kod değişikliği anında etkin olur

**Alternatifler**
- VSCode dev containers
- Google Colab
- PyCharm + local environment

**Trade-off**
- Büyük notebook’lar versiyon yönetiminde zorluk yaratabilir
- Jupyter dev environment GPU memory’yi prod kadar verimli kullanmayabilir

---

# 11. Configuration Structure

## **YAML config files (dev.yaml / prod.yaml)**
**Neden seçildi?**
- Dev ve prod ortam ayrımını *kod değiştirmeden* gerçekleştirme
- CI/CD veya K8s Job üzerinden override edilebilir parametreler
- `train.py` içinde central config loader kullanımı sadeleştirir

**Alternatifler**
- dotenv (.env) dosyaları
- JSON config
- Hydra config framework

**Trade-off**
- Çok kapsamlı projelerde Hydra gibi daha gelişmiş config yönetimi gerekebilir

---

# 12. Scheduler Behaviour

## **K8s PriorityClass**
**Neden seçildi?**
- GPU kaynakları sınırlı olduğunda *deterministic* önceliklendirme yapılır
- “prod > dev” queue mantığı manual bir scheduler yazmayı gereksiz kılar

**Alternatifler**
- Fair-share scheduler
- Custom controller/operator

**Trade-off**
- PriorityClass basit önceliklendirme sağlar; karmaşık kurallar için custom scheduler gerekir

---

# 13. Trade-off Özet Tablosu

| Bileşen | Avantaj | Dezavantaj |
|--------|---------|------------|
| K8s GPU Jobs | Standard, ölçeklenebilir | Setup & clustering maliyeti yüksek |
| HuggingFace | Hızlı fine-tune, geniş ekosistem | Çok büyük modeller GPU tüketir |
| MLflow | Basit, self-hosted | UI modern değil |
| S3/MinIO | Çok esnek | Local MinIO yönetimi gerekiyor |
| JupyterLab | DS için ideal | Notebook’lar code review zor |
| YAML config | Küçük projede ideal | Büyük projede config yönetimi büyür |
| Docker | Tutarlı environment | Base imageleri büyük |

---

# 14. Sonuç

Bu teknoloji seçimi:

- **Genişletilebilir**
- **Cloud veya on-prem uyumlu**
- **Minimum maliyetli**
- **Gerçek MLOps üretim senaryosuna uygun**
- **Case Study’nin tüm gereksinimlerini birebir karşılayan**

bir mimari ortaya koymaktadır.

Bu yaklaşım ile sistem:

- Dev ve prod arasında **sıfır kod değişikliği** ile geçiş yapabilir  
- GPU kaynaklarını otomatik olarak yönetir  
- Scheduler sayesinde 100+ kullanıcıya ölçeklenebilir  
- MLflow ve S3 sayesinde tüm deneylerin izlenebilirliği sağlanır  

Bu da case study’nin beklediği “scalable, efficient, clean” MLOps çözümünün temelini oluşturur.