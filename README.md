# ML Service — REST + gRPC + Streamlit + MinIO/DVC/MLflow

Сервис для обучения и инференса ML-моделей с REST API (FastAPI), gRPC и Streamlit-дашбордом.
Поддерживает несколько классов моделей (логистическая регрессия, случайный лес), хранит несколько обученных моделей, умеет переобучать и удалять модели.

Во 2-м ДЗ к этому добавилось:

* работа с S3 (MinIO),
* версионирование датасетов через DVC с remote в MinIO,
* сборка сервиса в Docker-образы,
* запуск всего стенда через `docker-compose` (API + gRPC + Streamlit + MinIO + MLflow),
* логирование обучения и моделей в MLflow (артефакты уходят в MinIO).

> Состав группы:
> – Галишникова Елизавета Дмитриевна (@egalishnikova)
> – Жильцов Алексей Павлович (@AleksaeZhiltsauff не коммитил, т.к. работаю на винде, с неё неудобно разрабатывать, поэтому разрабатывали и коммитили вместе с Лизой)

---

## Содержание

* [Что тут вообще происходит](#что-тут-вообще-происходит)
* [Требования](#требования)
* [Быстрая проверка “что всё живое”](#быстрая-проверка-что-всё-живое)
* [Установка и локальный запуск (Poetry, без Docker)](#установка-и-локальный-запуск-poetry-без-docker)

  * [Клонирование репозитория](#1-клонирование-репозитория)
  * [Создание окружения](#2-python-311-через-conda)
  * [Установка Poetry и зависимостей](#3-установка-poetry)
  * [Запуск REST, gRPC и Streamlit](#5-запуск-rest-api-локально)
* [Запуск через docker-compose (HW2)](#запуск-через-docker-compose-hw2-minio--mlflow--сервисы)

  * [Что поднимется](#что-именно-поднимается-и-на-каких-портах)
  * [API-ключ](#api-ключ)
  * [Шаги запуска](#как-запустить)
* [Проверка работоспособности по шагам](#проверка-работоспособности-по-шагам)

  * [REST](#1-rest)
  * [gRPC](#2-grpc)
  * [Streamlit](#3-streamlit)
  * [MLflow](#4-mlflow)
  * [MinIO](#5-minio-s3)
  * [DVC](#6-dvc)
* [REST: эндпоинты и примеры](#rest-список-эндпоинтов-и-примеры)
* [gRPC: proto, сервер и клиент](#grpc-proto-сервер-и-клиент)
* [Тесты и стиль кода](#тесты-и-стиль-кода)
* [Хранилище моделей, данные и логирование](#хранилище-моделей-данные-и-логирование)
* [Структура проекта](#структура-проекта)

---

## Что тут вообще происходит

умеет:

* обучать разные ML-модели:

  * `logreg` — логистическая регрессия,
  * `random_forest` — случайный лес;
* настраивать гиперпараметры при обучении;
* хранить несколько обученных моделей и обращаться к ним по `model_id`;
* получать предсказания, переобучать модели, удалять их;
* работать через:

  * REST (FastAPI + Swagger),
  * gRPC (для интеграции между сервисами),
  * Streamlit (интерактивный дашборд).

Во втором ДЗ:

* датасеты обучения сохраняются и версионируются через DVC,
* DVC remote настроен на MinIO (S3-совместимое хранилище),
* обучение и модели логируются в MLflow,
* всё поднимается одной командой `docker compose up --build`.

---

## Требования

### Для локального запуска (без Docker)

* macOS / Linux / Windows
* Python 3.11
* Anaconda/Miniconda (для удобного управления окружением)
* Poetry
* Git
* Браузер для Swagger/Streamlit

### Для запуска HW2 через Docker

* Docker
* Docker Compose v2 (`docker compose ...`)

---

## Быстрая проверка “что всё живое”

Если хочется быстро понять, что всё работает от начала до конца:

```bash
# 1. Клонируем репозиторий и переходим в него
git clone https://github.com/egalishnikova/ML_ops.git
cd ML_ops

# 2. Поднимаем всё через docker-compose
docker compose up --build
# Эту вкладку терминала оставляем открытой, там будут логи

# 3. В другом терминале проверяем REST
curl -s http://127.0.0.1:8000/health
# → {"status":"ok"}

# 4. Обучаем модель через REST (нужен X-API-Key: secret)
curl -s -X POST http://127.0.0.1:8000/train \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: secret' \
  -d '{
    "model_class": "logreg",
    "hyperparams": {"C": 1.0, "max_iter": 200},
    "X": [[0,0],[1,1],[1,0],[0,1]],
    "y": [0,1,1,0],
    "model_name": "demo-hw2"
  }'
```

После этого можно открыть:

* Swagger:  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Streamlit: [http://127.0.0.1:8501](http://127.0.0.1:8501)
* MLflow:    [http://127.0.0.1:5001](http://127.0.0.1:5001)
* MinIO:     [http://127.0.0.1:9001](http://127.0.0.1:9001)

В MLflow в эксперименте `ml-service` появится run с параметрами и метриками.
В MinIO в бакете `mlflow` появятся артефакты.

---

## Установка и локальный запуск (Poetry, без Docker)

Этот вариант ближе к первому ДЗ: запускается только приложение (без MinIO и MLflow).

### 1. Клонирование репозитория

```bash
git clone https://github.com/egalishnikova/ML_ops.git
cd ML_ops
```

Если хочется через GitHub CLI:

```bash
gh repo clone egalishnikova/ML_ops
cd ML_ops
```

### 2. Python 3.11 через conda

```bash
conda create -n mlops311 python=3.11 -y
conda activate mlops311
python --version  # ожидается 3.11.x
```

### 3. Установка Poetry

Один раз на системе:

```bash
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

poetry --version
```

(Если используете bash, вместо `~/.zshrc` нужно прописать в `~/.bashrc`.)

### 4. Установка зависимостей проекта

Из корня репозитория:

```bash
# привязать Poetry к python из активного окружения
poetry env use "$(which python)"

# установить зависимости (по poetry.lock)
poetry install --no-root
```

### 5. Запуск REST API (локально)

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

* Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Redoc:   [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Если переменная окружения `API_KEY` не задана, авторизация по ключу отключена, и можно ходить к защищённым эндпоинтам без заголовка `X-API-Key`.

---

## Запуск через docker-compose (HW2: MinIO + MLflow + сервисы)

Это основной сценарий для 2-го ДЗ.
Поднимается:

* `api`       — REST API (FastAPI),
* `grpc`      — gRPC сервер,
* `streamlit` — Streamlit-дашборд,
* `minio`     — S3-совместимое хранилище,
* `mlflow`    — трекинг обучения,
* `minio_mc`  — helper-контейнер для создания бакетов.

### Что именно поднимается и на каких портах

* REST API:      `http://127.0.0.1:8000`
* Swagger:       `http://127.0.0.1:8000/docs`
* Streamlit UI:  `http://127.0.0.1:8501`
* MLflow UI:     `http://127.0.0.1:5001`
* MinIO Console: `http://127.0.0.1:9001`

### API-ключ

В `docker-compose.yml` у сервисов `api` и `grpc` задан:

```yaml
API_KEY=secret
```

Поэтому:

* для `/train`, `/predict`, `/models`, `/models/{id}/retrain`, `/models/{id}` нужно передавать заголовок:

  * `X-API-Key: secret`
* Streamlit тоже ожидает этот ключ (его нужно ввести в поле в сайдбаре),
* gRPC-клиенту ключ передаётся флагом `--api_key secret`.

### Как запустить

```bash
cd ML_ops

# на всякий случай всё сбросить
docker compose down

# собрать образы и поднять стенд
docker compose up --build
```

Эту вкладку терминала оставляем с логами.

Во второй вкладке можно проверить:

```bash
docker compose ps
```

Должны быть `Up`:

* `ml_api`
* `ml_grpc`
* `ml_streamlit`
* `mlflow`
* `minio`

`minio_mc` может быть в состоянии `Exited (0)` — это нормально, он одноразовый (создаёт бакеты).

Остановить всё:

```bash
docker compose down
```

---

## Проверка работоспособности по шагам

### 1. REST

```bash
# health-check
curl -s http://127.0.0.1:8000/health
# → {"status":"ok"}

# список доступных классов моделей
curl -s http://127.0.0.1:8000/models/classes
# → ["logreg","random_forest"]
```

Обучение модели:

```bash
curl -s -X POST http://127.0.0.1:8000/train \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: secret' \
  -d '{
    "model_class": "logreg",
    "hyperparams": {"C": 1.0, "max_iter": 200},
    "X": [[0,0],[1,1],[1,0],[0,1]],
    "y": [0,1,1,0],
    "model_name": "full-check-demo"
  }'
```

Из ответа забираем `model_id` и проверяем предсказание:

```bash
curl -s -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: secret' \
  -d "{
    \"model_id\": \"<MODEL_ID>\",
    \"X\": [[1,1],[0,0]]
  }"
```

Ожидается, что вернутся `predictions` и `proba`.

### 2. gRPC

Пока `docker compose up` работает, из корня проекта:

```bash
# health
poetry run python -m clients.grpc_client health --api_key secret

# обучение
poetry run python -m clients.grpc_client train \
  --model_class logreg \
  --hyperparams '{"C":1.0,"max_iter":300}' \
  --X '[[0,0],[1,1],[1,0],[0,1]]' \
  --y '[0,1,1,0]' \
  --model_name demo-grpc \
  --api_key secret

# список моделей
poetry run python -m clients.grpc_client list-models --api_key secret
```

### 3. Streamlit

1. Открыть: `http://127.0.0.1:8501`.
2. В сайдбаре ввести API key: `secret`.
3. На вкладке `Health` проверить статус сервиса.
4. На вкладке `Train`:

   * выбрать класс модели,
   * задать X и y,
   * обучить модель.
5. На вкладке `Predict`:

   * указать `model_id`,
   * задать X,
   * получить предсказания.
6. На вкладке `Models` посмотреть список сохранённых моделей.

### 4. MLflow

Открыть: `http://127.0.0.1:5001`.

* в списке Experiments должен появиться `ml-service`,
* внутри — runs (например, `full-check-demo`, `demo-grpc`, тренировки из Streamlit),
* для каждого run:

  * вкладка `Metrics` — метрика `train_accuracy`,
  * вкладка `Params` — гиперпараметры и класс модели,
  * вкладка `Artifacts`:

    * `datasets/...` — JSON с X/y,
    * `model/...` — сохранённая модель (sklearn).

### 5. MinIO (S3)

Открыть: `http://127.0.0.1:9001`.

Логин: `minioadmin`
Пароль: `minioadmin`

В списке бакетов:

* `mlflow` — артефакты MLflow,
* `dvc` — remote для DVC (по нему настроен `.dvc/config`).

Можно открыть бакет `mlflow`, найти артефакты конкретного run’а (dataset и модель).

### 6. DVC

Локально в репозитории:

* существует `.dvc/` и `.dvc/config`,
* remote настроен на MinIO (`s3://dvc` с `endpointurl = http://minio:9000`),
* датасеты складываются в `data/datasets`.

Сервис при `/train`:

* сохраняет датасет в файл,
* пытается вызвать `dvc add` и `dvc push`,
* ошибки DVC логируются и не ломают API (обучение всё равно завершается успешно).

При необходимости можно вручную выполнить `dvc push` внутри контейнера `api`:

```bash
docker compose exec api dvc push
```

---

## REST: список эндпоинтов и примеры

Базовый URL: `http://127.0.0.1:8000`.

Авторизация:

* в docker-compose: `X-API-Key: secret` обязательно для защищённых эндпоинтов,
* в локальном запуске (без `API_KEY` в окружении) авторизация отключена.

| Метод  | Путь                         | Описание                          | Требует API-ключ |
| ------ | ---------------------------- | --------------------------------- | ---------------- |
| GET    | `/health`                    | Статус сервиса                    | нет              |
| GET    | `/models/classes`            | Список доступных классов моделей  | нет              |
| GET    | `/models`                    | Список обученных моделей          | да               |
| POST   | `/train`                     | Обучить модель                    | да               |
| POST   | `/predict`                   | Предсказание по конкретной модели | да               |
| POST   | `/models/{model_id}/retrain` | Переобучить существующую модель   | да               |
| DELETE | `/models/{model_id}`         | Удалить модель                    | да               |

Примеры `curl` уже приведены выше в разделе проверки.

---

## gRPC: proto, сервер и клиент

Файлы:

* Proto: `app/proto/model_service.proto`,
* Сгенерированные Python-файлы:

  * `app/proto/model_service_pb2.py`,
  * `app/proto/model_service_pb2_grpc.py`.

В `app/proto/__init__.py` есть, импорты настроены на относительные (`from . import model_service_pb2`), чтобы всё корректно работало и локально, и в докере.

### Перегенерация gRPC (если потребуется)

```bash
poetry run python -m grpc_tools.protoc \
  -I app/proto \
  --python_out=app/proto \
  --grpc_python_out=app/proto \
  app/proto/model_service.proto
```

### gRPC сервер локально

```bash
poetry run python -m app.grpc_server --host 0.0.0.0 --port 50051
```

В docker-compose gRPC-сервер поднимается автоматически.

### gRPC клиент

Скрипт: `clients/grpc_client.py`.

Примеры:

```bash
# health
poetry run python -m clients.grpc_client health --api_key secret

# список поддерживаемых классов моделей
poetry run python -m clients.grpc_client list-classes --api_key secret

# обучение
poetry run python -m clients.grpc_client train \
  --model_class logreg \
  --hyperparams '{"C":1.0,"max_iter":300}' \
  --X '[[0,0],[1,1],[1,0],[0,1]]' \
  --y '[0,1,1,0]' \
  --model_name demo-grpc \
  --api_key secret

# список обученных моделей
poetry run python -m clients.grpc_client list-models --api_key secret

# предсказание
poetry run python -m clients.grpc_client predict \
  --model_id <MODEL_ID> \
  --X '[[1,1],[0,0]]' \
  --api_key secret

# переобучение
poetry run python -m clients.grpc_client retrain \
  --model_id <MODEL_ID> \
  --X '[[0,0],[1,1]]' \
  --y '[0,1]' \
  --api_key secret

# удаление
poetry run python -m clients.grpc_client delete \
  --model_id <MODEL_ID> \
  --api_key secret
```

---

## Тесты и стиль кода

### Тесты

```bash
cd ML_ops
poetry run pytest -q
```

Тест `tests/test_api.py`:

* поднимает временный uvicorn-сервер на `127.0.0.1:8001`,
* прогоняет сценарий:

  * `/health`,
  * `/models/classes`,
  * `/train`,
  * `/predict`,
* проверяет, что всё отрабатывает и приходит разумный ответ.

Для pytest настроен `pytest.ini` с:

```ini
[pytest]
pythonpath = .
```

### Стиль кода

Линтер:

```bash
poetry run ruff check .
```

Часть замечаний ruff можно игнорировать (например, некоторые предпочтения стиля), критичные моменты поправлены.

---

## Хранилище моделей, данные и логирование

* Модели: `storage/models/<model_id>.joblib`
* Реестр моделей: `storage/registry.json`
* Логи приложения: `app.log`
* Датасеты (для DVC): `data/datasets/*.json`
* DVC-конфиг: `.dvc/config` (remote MinIO)
* DVC служебные файлы: `.dvc/`

Очистка локального состояния (осторожно):

```bash
rm -rf storage/models/* storage/registry.json app.log data/datasets/*
```

---

## Структура проекта

Кратко по основным частям:

```text
ML_ops/
├── app/
│   ├── __init__.py
│   ├── config.py              # настройки, логирование, API-ключ, MLflow, DVC
│   ├── main.py                # FastAPI (REST API)
│   ├── grpc_server.py         # gRPC сервер
│   ├── models_registry.py     # реестр и хранение моделей
│   ├── schemas.py             # Pydantic-схемы запросов/ответов
│   ├── ml/
│   │   ├── __init__.py
│   │   └── trainer.py         # обучение моделей, фабрика моделей
│   └── proto/
│       ├── __init__.py
│       ├── model_service.proto
│       ├── model_service_pb2.py
│       └── model_service_pb2_grpc.py
├── clients/
│   ├── __init__.py
│   └── grpc_client.py         # gRPC клиент
├── dashboard/
│   └── streamlit_app.py       # Streamlit-дашборд
├── data/
│   └── datasets/              # датасеты для DVC
├── storage/
│   ├── models/                # файлы моделей
│   └── registry.json          # создаётся автоматически
├── tests/
│   └── test_api.py            # smoke-тест REST API
├── .dvc/                      # служебное для DVC
├── .dvcignore
├── docker-compose.yml         # запуск стенда HW2
├── pyproject.toml             # Poetry + зависимости
├── poetry.lock
├── pytest.ini
├── .gitignore
└── README.md
```

---
