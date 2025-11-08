from __future__ import annotations

import asyncio
from threading import Thread

import httpx
import uvicorn

from app.main import app


def _run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")


def test_train_predict_smoke():
    # поднимаем сервер в фоне для теста
    th = Thread(target=_run_server, daemon=True)
    th.start()

    async def scenario():
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8001") as client:
            # health
            r = await client.get("/health")
            assert r.status_code == 200
            # classes
            r = await client.get("/models/classes")
            assert r.status_code == 200
            # train
            payload = {
                "model_class": "logreg",
                "hyperparams": {"max_iter": 200},
                "X": [[0,0],[1,1],[1,0],[0,1]],
                "y": [0,1,1,0],
                "model_name": "pytest"
            }
            r = await client.post("/train", json=payload, headers={})
            assert r.status_code == 200
            model_id = r.json()["model_id"]
            # predict
            r = await client.post("/predict", json={"model_id": model_id, "X": [[1,1],[0,0]]})
            assert r.status_code == 200
            body = r.json()
            assert "predictions" in body

    asyncio.run(scenario())