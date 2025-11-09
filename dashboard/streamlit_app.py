from __future__ import annotations

import argparse
import json
from typing import List, Optional

import requests
import streamlit as st


def post(url: str, payload: dict, api_key: Optional[str]):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()


def get(url: str, api_key: Optional[str]):
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def main(api_url: str, api_key: Optional[str]):
    st.set_page_config(page_title="ML Service Dashboard", layout="centered")
    st.title("ML Service Dashboard")

    with st.sidebar:
        st.header("Настройки")
        st.write(f"REST API: {api_url}")
        api_key = st.text_input("API Key (опционально)", value=api_key or "", type="password") or None

    tabs = st.tabs(["Health", "Train", "Predict", "Models"])

    with tabs[0]:
        if st.button("Проверить статус"):
            data = get(f"{api_url}/health", api_key)
            st.success(data)

    with tabs[1]:
        st.subheader("Обучение модели")
        classes = get(f"{api_url}/models/classes", None)
        model_class = st.selectbox("Класс модели", classes)
        model_name = st.text_input("Имя модели", value="streamlit-demo")
        hyper_raw = st.text_area("Гиперпараметры (JSON)", value="{}")
        X_raw = st.text_area("X (список списков)", value="[[0,0],[1,1],[1,0],[0,1]]")
        y_raw = st.text_input("y (список)", value="[0,1,1,0]")

        if st.button("Обучить"):
            try:
                hyper = json.loads(hyper_raw)
                X = json.loads(X_raw)
                y = json.loads(y_raw)
                resp = post(f"{api_url}/train", {"model_class": model_class, "hyperparams": hyper, "X": X, "y": y, "model_name": model_name}, api_key)  # noqa: E501
                st.success(resp)
            except Exception as e:  # noqa: BLE001
                st.error(str(e))

    with tabs[2]:
        st.subheader("Предсказание")
        model_id = st.text_input("Model ID")
        X_raw = st.text_area("X (список списков)", value="[[1,1],[0,0]]")
        if st.button("Предсказать"):
            try:
                X = json.loads(X_raw)
                resp = post(f"{api_url}/predict", {"model_id": model_id, "X": X}, api_key)
                st.success(resp)
            except Exception as e:  # noqa: BLE001
                st.error(str(e))

    with tabs[3]:
        st.subheader("Модели")
        if st.button("Обновить список"):
            try:
                items = get(f"{api_url}/models", api_key)
                st.table(items)
            except Exception as e:  # noqa: BLE001
                st.error(str(e))

if __name__ == "__main__":
    # Streamlit запускает скрипт как обычный Python-модуль и кладёт свои флаги в sys.argv.
    # Берём только то, что нам надо, а остальное игнорируем.
    import argparse
    import sys

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--api-key", default=None)

    # parse_known_args — чтобы не конфликтовать с внутренними флагами streamlit
    args, _ = parser.parse_known_args(sys.argv[1:])

    # Запускаем приложение
    main(api_url=args.api_url, api_key=args.api_key)
