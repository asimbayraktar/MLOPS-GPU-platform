import argparse
import yaml
import os
import random
import numpy as np

from dataset import load_raw_datasets
from model import load_model_and_tokenizer, train_model

# Opsiyonel: MLflow yoksa da çalışsın diye try/except
try:
    from utils.logging_utils import init_mlflow
except ImportError:
    def init_mlflow(cfg):
        return None


def set_seed(seed: int = 42):
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def parse_args():
    parser = argparse.ArgumentParser(description="Config-driven fine-tuning pipeline")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file (e.g. config/dev.yaml or config/prod.yaml)",
    )
    return parser.parse_args()


def load_config(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg


def main():
    args = parse_args()
    cfg = load_config(args.config)

    seed = cfg.get("seed", 42)
    set_seed(seed)

    # MLflow init (opsiyonel)
    mlflow_run = init_mlflow(cfg)

    # 1) Raw dataset yükle (text, label listeleri)
    train_texts, train_labels, val_texts, val_labels = load_raw_datasets(cfg)

    # 2) Model & tokenizer
    num_labels = len(set(train_labels))
    tokenizer, model = load_model_and_tokenizer(cfg, num_labels=num_labels)

    # 3) Eğit
    train_model(
        cfg=cfg,
        tokenizer=tokenizer,
        model=model,
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=val_texts,
        val_labels=val_labels,
        mlflow_run=mlflow_run,
    )

    # MLflow run kapatma (varsa)
    if mlflow_run is not None:
        import mlflow
        mlflow.end_run()

    print("✅ Training completed successfully!")


if __name__ == "__main__":
    main()