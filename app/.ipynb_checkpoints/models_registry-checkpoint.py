"""Реестр и хранение моделей.

Сохраняем модели в `storage/models/<model_id>.joblib` + метаданные в `registry.json`.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, Optional

import joblib

from .config import settings

logger = logging.getLogger(__name__)


@dataclass
class ModelRecord:
    model_id: str
    model_class: str
    model_name: Optional[str]
    path: str


class ModelRegistry:
    def __init__(self, registry_path: str) -> None:
        self.registry_path = registry_path
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.records: Dict[str, ModelRecord] = {
                    k: ModelRecord(**v) for k, v in data.items()
                }
        else:
            self.records = {}

    def _save(self) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump({k: asdict(v) for k, v in self.records.items()}, f, ensure_ascii=False, indent=2)

    def create(self, model_class: str, model_name: Optional[str]) -> ModelRecord:
        model_id = str(uuid.uuid4())
        path = os.path.join(settings.storage_dir, "models", f"{model_id}.joblib")
        rec = ModelRecord(model_id=model_id, model_class=model_class, model_name=model_name, path=path)
        self.records[model_id] = rec
        self._save()
        logger.info("Model created: %s (%s)", model_id, model_class)
        return rec

    def get(self, model_id: str) -> ModelRecord:
        rec = self.records.get(model_id)
        if not rec:
            raise KeyError(f"Model {model_id} not found")
        return rec

    def delete(self, model_id: str) -> None:
        rec = self.get(model_id)
        if os.path.exists(rec.path):
            os.remove(rec.path)
        del self.records[model_id]
        self._save()
        logger.info("Model deleted: %s", model_id)

    def list(self) -> Dict[str, ModelRecord]:
        return self.records

    @staticmethod
    def save_model(path: str, model) -> None:  # noqa: ANN001
        joblib.dump(model, path)

    @staticmethod
    def load_model(path: str):  # noqa: ANN001
        return joblib.load(path)