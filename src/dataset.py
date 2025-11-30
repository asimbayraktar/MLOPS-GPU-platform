import os
import csv
from typing import List, Tuple
from math import floor
import random


def _read_csv(path: str) -> Tuple[List[str], List[int]]:
    texts = []
    labels = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "text" not in reader.fieldnames or "label" not in reader.fieldnames:
            raise ValueError(
                f"{path} must contain 'text' and 'label' columns. Found: {reader.fieldnames}"
            )
        for row in reader:
            texts.append(row["text"])
            labels.append(int(row["label"]))
    return texts, labels


def _train_val_split(
    texts: List[str], labels: List[int], val_ratio: float = 0.2, seed: int = 42
) -> Tuple[List[str], List[int], List[str], List[int]]:
    random.seed(seed)
    indices = list(range(len(texts)))
    random.shuffle(indices)
    split_idx = floor(len(indices) * (1 - val_ratio))

    train_idx = indices[:split_idx]
    val_idx = indices[split_idx:]

    train_texts = [texts[i] for i in train_idx]
    train_labels = [labels[i] for i in train_idx]
    val_texts = [texts[i] for i in val_idx]
    val_labels = [labels[i] for i in val_idx]

    return train_texts, train_labels, val_texts, val_labels


def load_raw_datasets(cfg) -> Tuple[List[str], List[int], List[str], List[int]]:
    """
    Config format örneği:

    data:
      dataset_path: "./data/sample-small"   # klasör veya .csv
      format: "csv"
      val_ratio: 0.2

    Eski config ile uyumluluk için training.dataset_path de desteklenir.
    """

    data_cfg = cfg.get("data", {})
    dataset_path = data_cfg.get("dataset_path") or cfg.get("training", {}).get(
        "dataset_path"
    )
    if dataset_path is None:
        raise ValueError("dataset_path must be provided in config.data or config.training")

    val_ratio = data_cfg.get("val_ratio", 0.2)
    seed = cfg.get("seed", 42)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")

    # Eğer klasör ise train.csv & val.csv arıyoruz
    if os.path.isdir(dataset_path):
        train_path = os.path.join(dataset_path, "train.csv")
        val_path = os.path.join(dataset_path, "val.csv")

        if not os.path.exists(train_path):
            raise FileNotFoundError(f"Expected train.csv at {train_path}")

        train_texts, train_labels = _read_csv(train_path)

        if os.path.exists(val_path):
            val_texts, val_labels = _read_csv(val_path)
        else:
            # val.csv yoksa train'den split et
            train_texts, train_labels, val_texts, val_labels = _train_val_split(
                train_texts, train_labels, val_ratio, seed
            )

    # Tek bir CSV dosyası ise 80/20 split
    elif dataset_path.endswith(".csv"):
        texts, labels = _read_csv(dataset_path)
        train_texts, train_labels, val_texts, val_labels = _train_val_split(
            texts, labels, val_ratio, seed
        )
    else:
        raise ValueError(
            f"Unsupported dataset_path format: {dataset_path}. "
            "Provide a directory with train.csv[/val.csv] or a single .csv file."
        )

    return train_texts, train_labels, val_texts, val_labels