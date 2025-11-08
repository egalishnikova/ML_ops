from __future__ import annotations

import argparse
import json
import logging
from concurrent import futures
from typing import Dict

import grpc

from .config import check_api_key, configure_logging, ensure_dirs
from .models_registry import ModelRegistry
from .ml.trainer import get_available_model_classes, predict, train_model
from .proto import model_service_pb2 as pb2
from .proto import model_service_pb2_grpc as pb2_grpc

ensure_dirs()
configure_logging()
logger = logging.getLogger(__name__)
registry = ModelRegistry("storage/registry.json")


def _parse_hyperparams(h: Dict[str, str]) -> Dict:
    # простенький парсер: пытаемся json.loads, иначе оставляем как строку
    out = {}
    for k, v in h.items():
        try:
            out[k] = json.loads(v)
        except Exception:  # noqa: BLE001
            out[k] = v
    return out


class Service(pb2_grpc.ModelServiceServicer):
    def Health(self, request, context):  # noqa: N802
        try:
            check_api_key(getattr(request, "api_key", None))
        except PermissionError as e:  # noqa: BLE001
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        return pb2.HealthResponse(status="ok")

    def ListModelClasses(self, request, context):  # noqa: N802
        classes = get_available_model_classes()
        return pb2.ModelClassesResponse(classes=classes)

    def ListModels(self, request, context):  # noqa: N802
        items = []
        for rec in registry.list().values():
            items.append(
                pb2.ModelInfo(model_id=rec.model_id, model_class=rec.model_class, model_name=rec.model_name)
            )
        return pb2.ListModelsResponse(items=items)

    def Train(self, request, context):  # noqa: N802
        try:
            check_api_key(getattr(request, "api_key", None))
        except PermissionError as e:  # noqa: BLE001
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        X = [fa.values for fa in request.X]
        y = list(request.y)
        model, metrics = train_model(request.model_class, _parse_hyperparams(request.hyperparams), X, y)
        rec = registry.create(request.model_class, request.model_name or None)
        registry.save_model(rec.path, model)
        return pb2.TrainResponse(
            model_id=rec.model_id,
            model_class=rec.model_class,
            model_name=rec.model_name or "",
            metrics=metrics,
        )

    def Predict(self, request, context):  # noqa: N802
        try:
            check_api_key(getattr(request, "api_key", None))
        except PermissionError as e:  # noqa: BLE001
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        rec = registry.get(request.model_id)
        model = registry.load_model(rec.path)
        X = [fa.values for fa in request.X]
        preds, proba = predict(model, X)
        proba_msgs = []
        if proba is not None:
            for row in proba:
                proba_msgs.append(pb2.ProbRow(values=row))
        return pb2.PredictResponse(predictions=preds, proba=proba_msgs)

    def Retrain(self, request, context):  # noqa: N802
        try:
            check_api_key(getattr(request, "api_key", None))
        except PermissionError as e:  # noqa: BLE001
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        rec = registry.get(request.model_id)
        X = [fa.values for fa in request.X]
        y = list(request.y)
        model, metrics = train_model(rec.model_class, _parse_hyperparams(request.hyperparams), X, y)
        registry.save_model(rec.path, model)
        return pb2.TrainResponse(
            model_id=rec.model_id,
            model_class=rec.model_class,
            model_name=rec.model_name or "",
            metrics=metrics,
        )

    def Delete(self, request, context):  # noqa: N802
        try:
            check_api_key(getattr(request, "api_key", None))
        except PermissionError as e:  # noqa: BLE001
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        registry.delete(request.model_id)
        return pb2.DeleteResponse(status="deleted", model_id=request.model_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50051)
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_ModelServiceServicer_to_server(Service(), server)
    server.add_insecure_port(f"{args.host}:{args.port}")
    logger.info("Starting gRPC server on %s:%s", args.host, args.port)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    main()