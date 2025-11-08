"""Фабрика моделей и процессы обучения/предсказания."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

SUPPORTED_MODELS = {
    "logreg": LogisticRegression,
    "random_forest": RandomForestClassifier,
}


def get_available_model_classes() -> List[str]:
    return sorted(list(SUPPORTED_MODELS.keys()))


def build_model(model_class: str, hyperparams: Dict[str, Any]):
    if model_class not in SUPPORTED_MODELS:
        raise ValueError(f"Unknown model_class '{model_class}'")
    cls = SUPPORTED_MODELS[model_class]
    return cls(**hyperparams)


def train_model(model_class: str, hyperparams: Dict[str, Any], X: List[List[float]], y: List[int]):
    X_np = np.array(X)
    y_np = np.array(y)
    model = build_model(model_class, hyperparams)
    model.fit(X_np, y_np)
    preds = model.predict(X_np)
    acc = float(accuracy_score(y_np, preds))
    metrics = {"train_accuracy": acc}
    return model, metrics


def predict(model, X: List[List[float]]) -> Tuple[List[int], List[List[float]] | None]:  # noqa: ANN001
    X_np = np.array(X)
    preds = model.predict(X_np)
    proba = None
    if hasattr(model, "predict_proba"):
        proba_np = model.predict_proba(X_np)
        proba = proba_np.tolist()
    return preds.tolist(), proba