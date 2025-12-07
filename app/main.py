"""FastAPI приложение с REST эндпоинтами."""
from __future__ import annotations

import logging
import os
import json
import uuid
import subprocess
from typing import Dict, List

from fastapi import Depends, FastAPI, Header, HTTPException, status

from .config import check_api_key, configure_logging, ensure_dirs, settings
from .models_registry import ModelRegistry
from .ml.trainer import get_available_model_classes, predict, train_model
from .schemas import (
    ModelInfo,
    PredictRequest,
    PredictResponse,
    RetrainRequest,
    TrainRequest,
    TrainResponse,
)

import mlflow
import mlflow.sklearn

# Подготовка окружения, логгирование
ensure_dirs()
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service", version="0.1.0")
registry = ModelRegistry("storage/registry.json")


def _auth(x_api_key: str | None = Header(default=None)) -> None:
    try:
        check_api_key(x_api_key)
    except PermissionError as e:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


def _ensure_data_dir() -> None:
    os.makedirs(settings.data_dir, exist_ok=True)


def _save_dataset_to_file(X, y) -> str:
    _ensure_data_dir()
    file_path = os.path.join(settings.data_dir, f"trainset_{uuid.uuid4().hex}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"X": X, "y": y}, f)
    return file_path


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def _dvc_track_and_push(path: str) -> None:
    if not settings.enable_dvc:
        return
    try:
        _run(["dvc", "add", path])
        _run(["git", "add", f"{path}.dvc", ".gitignore"])
        _run(["git", "commit", "-m", f"data: add {os.path.basename(path)} via dvc"])
        _run(["dvc", "push"])
    except Exception as e:  # noqa: BLE001
        logger.warning("DVC push skipped: %s", e)


@app.get("/health", tags=["system"])
def health() -> Dict[str, str]:
    """Статус сервиса."""
    logger.info("Health check")
    return {"status": "ok"}


@app.get("/models/classes", tags=["models"])
def list_model_classes() -> List[str]:
    """Список доступных классов моделей."""
    return get_available_model_classes()


@app.get("/models", tags=["models"], response_model=List[ModelInfo])
def list_models(_: None = Depends(_auth)) -> List[ModelInfo]:
    """Список обученных моделей."""
    return [
        ModelInfo(model_id=rec.model_id, model_class=rec.model_class, model_name=rec.model_name)
        for rec in registry.list().values()
    ]


@app.post("/train", tags=["train"], response_model=TrainResponse)
def train(req: TrainRequest, _: None = Depends(_auth)) -> TrainResponse:
    """Обучить модель и сохранить её в хранилище."""
    logger.info("Train request: class=%s name=%s", req.model_class, req.model_name)

    # базовое обучение
    model, metrics = train_model(req.model_class, req.hyperparams, req.X, req.y)
    rec = registry.create(req.model_class, req.model_name)
    registry.save_model(rec.path, model)

    # 1) сохраняем датасет и (опц.) отправляем в DVC
    dataset_path = None
    try:
        dataset_path = _save_dataset_to_file(req.X, req.y)
        _dvc_track_and_push(dataset_path)
    except Exception as e:  # noqa: BLE001
        logger.warning("Dataset save / DVC push skipped: %s", e)

    # 2) логируем в MLflow (если включено)
    if settings.enable_mlflow:
        try:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            mlflow.set_experiment("ml-service")
            with mlflow.start_run(run_name=req.model_name or rec.model_id):
                # параметры
                params = {"model_class": req.model_class}
                params.update(req.hyperparams)
                mlflow.log_params(params)

                # метрики
                if metrics:
                    for k, v in metrics.items():
                        if isinstance(v, (int, float)):
                            mlflow.log_metric(k, float(v))

                # датасет как артефакт
                if dataset_path is not None:
                    mlflow.log_artifact(dataset_path, artifact_path="datasets")

                # модель как артефакт
                try:
                    mlflow.sklearn.log_model(model, artifact_path="model")
                except Exception as e:  # noqa: BLE001
                    logger.warning("MLflow log_model skipped: %s", e)

                # теги
                mlflow.set_tags(
                    {
                        "model_id": rec.model_id,
                        "model_name": rec.model_name or "",
                        "model_class": rec.model_class,
                    }
                )
        except Exception as e:  # noqa: BLE001
            logger.warning("MLflow logging skipped: %s", e)

    return TrainResponse(
        model_id=rec.model_id,
        model_class=rec.model_class,
        model_name=rec.model_name,
        metrics=metrics,
    )


@app.post("/predict", tags=["predict"], response_model=PredictResponse)
def predict_endpoint(req: PredictRequest, _: None = Depends(_auth)) -> PredictResponse:
    """Получить предсказание уже обученной модели по `model_id`."""
    logger.info("Predict request: model_id=%s", req.model_id)
    rec = registry.get(req.model_id)
    model = registry.load_model(rec.path)
    preds, proba = predict(model, req.X)
    return PredictResponse(predictions=preds, proba=proba)


@app.post("/models/{model_id}/retrain", tags=["models"], response_model=TrainResponse)
def retrain(model_id: str, req: RetrainRequest, _: None = Depends(_auth)) -> TrainResponse:
    """Переобучить существующую модель заново (можно изменить гиперпараметры)."""
    logger.info("Retrain request: model_id=%s", model_id)
    rec = registry.get(model_id)
    model, metrics = train_model(rec.model_class, req.hyperparams, req.X, req.y)
    registry.save_model(rec.path, model)
    return TrainResponse(
        model_id=rec.model_id,
        model_class=rec.model_class,
        model_name=rec.model_name,
        metrics=metrics,
    )


@app.delete("/models/{model_id}", tags=["models"])
def delete_model(model_id: str, _: None = Depends(_auth)) -> Dict[str, str]:
    """Удалить обученную модель и запись в реестре."""
    logger.info("Delete request: model_id=%s", model_id)
    registry.delete(model_id)
    return {"status": "deleted", "model_id": model_id}
