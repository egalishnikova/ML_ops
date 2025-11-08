"""FastAPI приложение с REST эндпоинтами."""
from __future__ import annotations

import logging
from typing import Dict, List

from fastapi import Depends, FastAPI, Header, HTTPException, status

from .config import check_api_key, configure_logging, ensure_dirs
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
    model, metrics = train_model(req.model_class, req.hyperparams, req.X, req.y)
    rec = registry.create(req.model_class, req.model_name)
    registry.save_model(rec.path, model)
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