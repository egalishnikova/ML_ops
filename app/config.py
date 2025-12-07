import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    # --- базовые настройки хранилища/логов/авторизации ---
    storage_dir: str = os.getenv("STORAGE_DIR", "storage")
    models_dir: str = os.getenv("MODELS_DIR", os.path.join("storage", "models"))
    registry_path: str = os.getenv("REGISTRY_PATH", os.path.join("storage", "registry.json"))
    log_file: str = os.getenv("LOG_FILE", "app.log")
    api_key: Optional[str] = os.getenv("API_KEY")  # если None – авторизация выключена

    # --- S3 / MinIO ---
    s3_endpoint: str = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
    s3_access_key: str = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    s3_secret_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    s3_bucket_models: str = os.getenv("S3_BUCKET_MODELS", "mlflow")

    # --- MLflow ---
    mlflow_tracking_uri: Optional[str] = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://mlflow:5000",
    )
    enable_mlflow: bool = os.getenv("ENABLE_MLFLOW", "0") == "1"

    # --- DVC ---
    enable_dvc: bool = os.getenv("ENABLE_DVC", "0") == "1"
    data_dir: str = os.getenv("DATA_DIR", "data/datasets")


settings = Settings()


def ensure_dirs() -> None:
    """Создаёт базовые директории и файл реестра, если их ещё нет."""
    os.makedirs(settings.storage_dir, exist_ok=True)
    os.makedirs(settings.models_dir, exist_ok=True)

    reg_path = Path(settings.registry_path)
    if not reg_path.exists():
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        reg_path.write_text("{}", encoding="utf-8")

    # папка для датасетов (для DVC)
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)


def configure_logging() -> None:
    """Базовая настройка логгера: в файл + в консоль."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # чтобы не дублировать хендлеры при повторных вызовах
    root = logging.getLogger()
    if root.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.log_file),
        ],
    )


def check_api_key(value: Optional[str]) -> None:
    """Проверка API-ключа. Если ключ не задан в настройках — авторизация отключена."""
    if settings.api_key is None:
        return
    if value != settings.api_key:
        raise PermissionError("Invalid API key")
