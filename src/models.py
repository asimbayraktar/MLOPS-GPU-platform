from typing import List, Optional

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)


def load_model_and_tokenizer(cfg, num_labels: int):
    """
    Config örneği:

    model:
      pretrained_name: "distilbert-base-uncased"

    Yoksa default distilbert kullanılır.
    """
    model_cfg = cfg.get("model", {})
    pretrained_name = model_cfg.get("pretrained_name", "distilbert-base-uncased")

    tokenizer = AutoTokenizer.from_pretrained(pretrained_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        pretrained_name,
        num_labels=num_labels,
    )

    return tokenizer, model


def _encode_dataset(
    texts: List[str],
    labels: List[int],
    tokenizer,
    max_length: int = 128,
) -> Dataset:
    encodings = tokenizer(
        texts,
        truncation=True,
        padding="max_length",
        max_length=max_length,
    )
    encodings["labels"] = labels
    dataset = Dataset.from_dict(encodings)
    return dataset


def _compute_accuracy(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = (preds == labels).astype(np.float32).mean().item()
    return {"accuracy": acc}


def train_model(
    cfg,
    tokenizer,
    model,
    train_texts: List[str],
    train_labels: List[int],
    val_texts: List[str],
    val_labels: List[int],
    mlflow_run: Optional[object] = None,
):
    training_cfg = cfg.get("training", {})
    model_cfg = cfg.get("model", {})

    device = training_cfg.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    epochs = training_cfg.get("epochs", 1)
    batch_size = training_cfg.get("batch_size", 8)
    lr = training_cfg.get("learning_rate", 5e-5)
    output_dir = training_cfg.get("output_path", "./outputs")
    max_length = model_cfg.get("max_length", 128)

    model.to(device)

    # Dataset'i encode et
    train_dataset = _encode_dataset(train_texts, train_labels, tokenizer, max_length)
    val_dataset = _encode_dataset(val_texts, val_labels, tokenizer, max_length)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=lr,
        evaluation_strategy="epoch",
        logging_strategy="steps",
        logging_steps=training_cfg.get("logging_steps", 50),
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        report_to=[] if mlflow_run is None else ["none"],  # HF'nin kendi logger'ını sessize al
    )

    def compute_metrics(eval_pred):
        metrics = _compute_accuracy(eval_pred)
        # Opsiyonel: MLflow'a metric yolla
        if mlflow_run is not None:
            try:
                import mlflow

                for k, v in metrics.items():
                    mlflow.log_metric(k, v)
            except Exception:
                # Prod'da çökmemesi için defensif yaklaşım
                pass
        return metrics

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # Parametreleri MLflow'a logla (isteğe bağlı)
    if mlflow_run is not None:
        try:
            import mlflow

            mlflow.log_params(
                {
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "learning_rate": lr,
                    "max_length": max_length,
                    "device": device,
                }
            )
        except Exception:
            pass

    trainer.train()

    # Eğitilmiş modeli kaydet
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)