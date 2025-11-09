"""Pydantic‑схемы REST‑API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    model_class: str = Field(description="Класс модели: 'logreg' или 'random_forest'")
    hyperparams: Dict[str, Any] = Field(default_factory=dict)
    X: List[List[float]]
    y: List[int]
    model_name: Optional[str] = Field(default=None, description="Человекочитаемое имя модели")


class TrainResponse(BaseModel):
    model_id: str
    model_class: str
    model_name: Optional[str]
    metrics: Dict[str, float]


class PredictRequest(BaseModel):
    model_id: str
    X: List[List[float]]


class PredictResponse(BaseModel):
    predictions: List[int]
    proba: Optional[List[List[float]]] = None


class RetrainRequest(BaseModel):
    X: List[List[float]]
    y: List[int]
    hyperparams: Dict[str, Any] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    model_id: str
    model_class: str
    model_name: Optional[str] = None