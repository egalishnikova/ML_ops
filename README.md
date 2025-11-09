# ML Service — REST + gRPC + Streamlit (Poetry)

Сервис для **обучения и инференса ML-моделей** с REST API (FastAPI), gRPC и Streamlit-дашбордом.
Поддерживает **несколько классов моделей** (логистическая регрессия, случайный лес), **хранит несколько обученных моделей**, умеет **переобучать и удалять** модели. Есть логирование, Swagger/Redoc, тесты (pytest), линтер (ruff), пока НАДО ДОДЕЛАТЬ опциональная авторизация по API-ключу.

> **Состав группы:**
> – Галишникова Елизавета Дмитриевна (@egalishnikova)
> – Жильцов Алексей Павлович (@AleksaeZhiltsauff не коммитил, т.к. работаю на винде, с неё неудобно разрабатывать, поэтому разрабатывали и коммитили вместе с Лизой)

---

## Содержание

* [Требования](#требования)
* [Как работать с сервисом?](#быстрый-старт-tldr)
* [Установка и окружение](#установка-и-окружение-подробно)
* [Запуск сервисов](#запуск-сервисов)

  * [REST (FastAPI)](#rest-fastapi)
  * [gRPC](#grpc)
  * [Streamlit-дашборд](#streamlit-дашборд)
* [Проверка работоспособности](#проверка-работоспособности-чек-лист)
* [REST: список эндпоинтов и примеры](#rest-список-эндпоинтов-и-примеры)
* [gRPC: контракт, генерация и клиент](#grpc-контракт-генерация-и-клиент)
* [Тесты и стиль кода (тут есть куда улучшаться)](#тесты-и-стиль-кода)
* [Хранилище моделей и логирование](#хранилище-моделей-и-логирование)
* [Структура проекта](#структура-проекта)
* [Краткое содержание для нас самих](#краткое-содержание-для-нас-самих)

---

## Требования

* macOS / Linux / Windows (тестировали на macOS)
* **Python 3.11** 
* **Poetry**
* Git
* Браузер для Swagger/Streamlit

---

## Как работать с сервисом?

```bash
# 1) Клонировать репозиторий (пример через GitHub CLI)
gh repo clone egalishnikova/ML_ops
cd ML_ops

# 2) Создать окружение python 3.11 
conda create -n mlops311 python=3.11 -y
conda activate mlops311

# 3) Установить Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# 4) Установить зависимости проекта
poetry env use "$(which python)"
poetry install --no-root

# 5) Запустить REST API
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Swagger: http://127.0.0.1:8000/docs

# 6) В новом терминале: тренировка + предсказание (curl)
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/models/classes
curl -s -X POST http://127.0.0.1:8000/train -H 'Content-Type: application/json' \
  -d '{"model_class":"logreg","hyperparams":{"C":1.0,"max_iter":500},"X":[[0,0],[1,1],[1,0],[0,1]],"y":[0,1,1,0],"model_name":"demo"}'

# 7) gRPC сервер (в отдельном терминале)
poetry run python -m app.grpc_server --host 0.0.0.0 --port 50051

# 8) gRPC клиент (из корня; модель логрег)
poetry run python -m clients.grpc_client train \
  --model_class logreg \
  --hyperparams '{"C":1.0,"max_iter":300}' \
  --X '[[0,0],[1,1],[1,0],[0,1]]' \
  --y '[0,1,1,0]' \
  --model_name demo-grpc

# 9) Streamlit (опционально)
poetry run streamlit run dashboard/streamlit_app.py
```

---

## Установка и окружение

### 1) Клонирование репозитория

**Вариант A — GitHub CLI (рекомендуется):**

```bash
gh auth login            # один раз, затем:
gh repo clone egalishnikova/ML_ops
cd ML_ops
```

**Вариант B — HTTPS + токен:**

```bash
git clone https://<your_token>@github.com/egalishnikova/ML_ops.git
cd ML_ops
```

### 2) Python 3.11 (через conda)

```bash
conda create -n mlops311 python=3.11 -y
conda activate mlops311
python --version  # 3.11.x
```

### 3) Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
# добавьте Poetry в PATH (macOS zsh):
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
poetry --version
```

> Если `poetry` «пропадает» в новых окнах терминала надо PATH добавить в `~/.zshrc` (а не только в `~/.zprofile`) (при разработке у нас была такая проблема; иначе нужно импортить poetry в каждый новый терминал)

### 4) Установка зависимостей проекта

```bash
# связать Poetry с python из conda-среды
poetry env use "$(which python)"

# установить зависимости и создать lock
poetry install --no-root

```

---

## Запуск сервисов

### REST (FastAPI)

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

* Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Redoc:  [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### gRPC

**Сервер:**

```bash
poetry run python -m app.grpc_server --host 0.0.0.0 --port 50051
```

**Клиент (скрипт):**

```bash
# обучение
poetry run python -m clients.grpc_client train \
  --model_class logreg \
  --hyperparams '{"C":1.0,"max_iter":300}' \
  --X '[[0,0],[1,1],[1,0],[0,1]]' \
  --y '[0,1,1,0]' \
  --model_name demo-grpc

# список моделей
poetry run python -m clients.grpc_client list-models

# предсказание (подставьте свой model_id)
poetry run python -m clients.grpc_client predict \
  --model_id <MODEL_ID> \
  --X '[[1,1],[0,0]]'
```

### Streamlit-дашборд

```bash
poetry run streamlit run dashboard/streamlit_app.py
# по умолчанию использует REST на http://127.0.0.1:8000
```

В браузере доступны вкладки: Health, Train, Predict, Models

---

## Проверка работоспособности (чек-лист)

1. **REST:**

   * Запустить uvicorn.
   * Открыть Swagger `/docs`.
   * `GET /health` → `{"status": "ok"}`
   * `GET /models/classes` → `["logreg","random_forest"]`
   * `POST /train` (см. ниже пример) → получить `model_id`.
   * `POST /predict` с `model_id` → получить предсказания.

2. **gRPC:**

   * Запустить gRPC-сервер.
   * Клиентом `train` → получить `model_id`.
   * Клиентом `predict` → увидеть предсказания.
   * Клиентом `list-models`/`list-classes` → получить списки.

3. **Streamlit:**

   * Запустить приложение.
   * Во вкладке Health → «Проверить статус».
   * Во вкладке Train → обучить модель.
   * Во вкладке Predict → предсказать по `model_id`.

4. **Тесты и стиль:**

   ```bash
   poetry run pytest -q     # должно быть green
   poetry run ruff check .  # без критичных ошибок
   ```

---

## REST: список эндпоинтов и примеры

Базовый URL: `http://127.0.0.1:8000`

|  Метод | Путь                         | Описание                        | Auth |
| -----: | ---------------------------- | ------------------------------- | :--: |
|    GET | `/health`                    | Статус сервиса                  |   –  |
|    GET | `/models/classes`            | Доступные классы моделей        |   –  |
|    GET | `/models`                    | Список обученных моделей        |   ✓  |
|   POST | `/train`                     | Обучить модель                  |   ✓  |
|   POST | `/predict`                   | Предсказание конкретной модели  |   ✓  |
|   POST | `/models/{model_id}/retrain` | Переобучить существующую модель |   ✓  |
| DELETE | `/models/{model_id}`         | Удалить модель                  |   ✓  |

### Примеры `curl`

**Проверка:**

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/models/classes
```

**Обучение (logreg):**

```bash
curl -s -X POST http://127.0.0.1:8000/train \
  -H 'Content-Type: application/json' \
  -d '{
    "model_class": "logreg",
    "hyperparams": {"C": 1.0, "max_iter": 500},
    "X": [[0,0],[1,1],[1,0],[0,1]],
    "y": [0,1,1,0],
    "model_name": "demo-logreg"
  }'
```

**Предсказание:**

```bash
curl -s -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d "{
    \"model_id\": \"<MODEL_ID>\",
    \"X\": [[1,1],[0,0]]
  }"
```

**Переобучение:**

```bash
curl -s -X POST http://127.0.0.1:8000/models/<MODEL_ID>/retrain \
  -H 'Content-Type: application/json' \
  -d '{"X": [[0,0],[1,1]], "y": [0,1], "hyperparams": {"C": 0.5}}'
```

**Удаление:**

```bash
curl -s -X DELETE http://127.0.0.1:8000/models/<MODEL_ID>
```

---

## gRPC: контракт, генерация и клиент

**Proto:** `app/proto/model_service.proto`
Сгенерированные файлы: `app/proto/model_service_pb2.py`, `app/proto/model_service_pb2_grpc.py` (уже в репозитории).

**Перегенерация (не требуется для запуска):**

```bash
poetry run python -m grpc_tools.protoc \
  -I app/proto \
  --python_out=app/proto \
  --grpc_python_out=app/proto \
  app/proto/model_service.proto
```

> Обратите внимание: для корректных импортов `app/proto` содержит `__init__.py`, а в `model_service_pb2_grpc.py` используется относительный импорт:
> `from . import model_service_pb2 as model__service__pb2`

**gRPC сервер:**

```bash
poetry run python -m app.grpc_server --host 0.0.0.0 --port 50051
```

**gRPC клиент (готовый скрипт):**

```bash
poetry run python -m clients.grpc_client list-classes
poetry run python -m clients.grpc_client train --model_class logreg --hyperparams '{"C":1.0,"max_iter":300}' --X '[[0,0],[1,1],[1,0],[0,1]]' --y '[0,1,1,0]' --model_name demo-grpc
poetry run python -m clients.grpc_client predict --model_id <MODEL_ID> --X '[[1,1],[0,0]]'
poetry run python -m clients.grpc_client list-models
poetry run python -m clients.grpc_client retrain --model_id <MODEL_ID> --X '[[0,0],[1,1]]' --y '[0,1]'
poetry run python -m clients.grpc_client delete --model_id <MODEL_ID>
poetry run python -m clients.grpc_client health
```

---

## Тесты и стиль кода

```bash
# тесты
poetry run pytest -q

# линтер
poetry run ruff check .
```

При необходимости мы добавили `pytest.ini` с `pythonpath = .`, чтобы `app` корректно импортировался в тестах.
В тесте предусмотрено ожидание готовности `/health`, чтобы не падать на гонках старта.

---

## Хранилище моделей и логирование

* Модели сохраняются в: `storage/models/<model_id>.joblib`
* Реестр моделей: `storage/registry.json`
* Логи: `app.log` (и дублирование в консоль)

Очистить всё:

```bash
rm -rf storage/models/* storage/registry.json app.log
```
---

## Структура проекта

```
ML_ops/
├── app/
│   ├── __init__.py
│   ├── config.py              # настройки, логирование, проверка API ключа
│   ├── main.py                # FastAPI (REST)
│   ├── grpc_server.py         # gRPC сервер
│   ├── models_registry.py     # реестр/сохранение моделей
│   ├── schemas.py             # Pydantic схемы
│   ├── ml/
│   │   ├── __init__.py
│   │   └── trainer.py         # фабрика и обучение моделей
│   └── proto/
│       ├── __init__.py
│       ├── model_service.proto
│       ├── model_service_pb2.py
│       └── model_service_pb2_grpc.py
├── clients/
│   ├── __init__.py
│   ├── grpc_client.py         # gRPC клиент
│   └── examples.http          # примеры REST запросов (VSCode/IntelliJ)
├── dashboard/
│   └── streamlit_app.py       # Streamlit дашборд
├── storage/
│   ├── models/                # файлы моделей
│   └── registry.json          # создаётся автоматически
├── tests/
│   └── test_api.py            # smoke-тест REST
├── pyproject.toml             # Poetry + ruff
├── poetry.lock
├── pytest.ini
├── .gitignore
└── README.md
```

## Краткое содержание для нас самих

Короче напсианный сервис — это что-то вроде мини-“ML-хаба”, т.к. через него можно обучать разные модели, сохранять их, предсказывать, переобучать и удалять, всё это — через REST (для людей и HTTP-запросов), gRPC (для машин и быстрой интеграции) или Streamlit-дашборд (для наглядной UIки)

Главные фичи:

- работает из коробки через FastAPI, gRPC и Streamlit

- хранит сколько угодно моделей, не теряя их между запусками

- можно играться с гиперпараметрами и быстро смотреть метрики

- красивый интерфейс в Swagger и Streamlit

- логирование всех действий + тесты, чтобы всё было стабильно

- использует Poetry вместо requirements.txt

