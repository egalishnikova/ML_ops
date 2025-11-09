"""Конфигурация приложения и вспомогательные функции.

Поддерживает загрузку окружения из .env. Включает простую проверку API ключа
для REST и gRPC (опционально).
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    api_key: Optional[str] = os.getenv("API_KEY")
    storage_dir: str = os.getenv("STORAGE_DIR", "storage")
    registry_path: str = os.getenv("REGISTRY_PATH", "storage/registry.json")
    log_path: str = os.getenv("LOG_PATH", "app.log")


settings = Settings()


def ensure_dirs() -> None:
    os.makedirs(settings.storage_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.storage_dir, "models"), exist_ok=True)
    if not os.path.exists(settings.registry_path):
        with open(settings.registry_path, "w", encoding="utf-8") as f:
            json.dump({}, f)


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(ch)

    # Rotating file
    fh = RotatingFileHandler(settings.log_path, maxBytes=2_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(fh)


def check_api_key(provided: Optional[str]) -> None:
    """Проверяет API ключ, если он включён.

    :raises PermissionError: если ключ требуется, но не передан/не совпадает
    """
    if settings.api_key:
        if not provided or provided != settings.api_key:
            raise PermissionError("Invalid or missing API key")