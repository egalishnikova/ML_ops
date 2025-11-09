from __future__ import annotations

import argparse
import json
from typing import List

import grpc

from app.proto import model_service_pb2 as pb2
from app.proto import model_service_pb2_grpc as pb2_grpc


def to_float_arrays(matrix: List[List[float]]):
    return [pb2.FloatArray(values=row) for row in matrix]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["train", "predict", "list-classes", "list-models", "retrain", "delete", "health"])  # noqa: E501
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--api_key", default=None)

    # common args
    parser.add_argument("--model_class")
    parser.add_argument("--hyperparams", default="{}")
    parser.add_argument("--X")
    parser.add_argument("--y")
    parser.add_argument("--model_id")
    parser.add_argument("--model_name", default=None)

    args = parser.parse_args()

    channel = grpc.insecure_channel(f"{args.host}:{args.port}")
    stub = pb2_grpc.ModelServiceStub(channel)

    if args.command == "list-classes":
        resp = stub.ListModelClasses(pb2.Empty())
        print(resp.classes)
        return

    if args.command == "list-models":
        resp = stub.ListModels(pb2.Empty())
        for item in resp.items:
            print(item)
        return

    if args.command == "health":
        resp = stub.Health(pb2.HealthRequest(api_key=args.api_key or ""))
        print(resp.status)
        return

    if args.command == "train":
        X = json.loads(args.X)
        y = json.loads(args.y)
        hyper = json.loads(args.hyperparams)
        req = pb2.TrainRequest(
            api_key=args.api_key or "",
            model_class=args.model_class,
            hyperparams={k: json.dumps(v) for k, v in hyper.items()},
            X=to_float_arrays(X),
            y=y,
            model_name=args.model_name or "",
        )
        resp = stub.Train(req)
        print(resp)
        return

    if args.command == "predict":
        X = json.loads(args.X)
        req = pb2.PredictRequest(api_key=args.api_key or "", model_id=args.model_id, X=to_float_arrays(X))
        resp = stub.Predict(req)
        print(resp)
        return

    if args.command == "retrain":
        X = json.loads(args.X)
        y = json.loads(args.y)
        hyper = json.loads(args.hyperparams) if args.hyperparams else {}
        req = pb2.RetrainRequest(
            api_key=args.api_key or "",
            model_id=args.model_id,
            X=to_float_arrays(X),
            y=y,
            hyperparams={k: json.dumps(v) for k, v in hyper.items()},
        )
        resp = stub.Retrain(req)
        print(resp)
        return

    if args.command == "delete":
        req = pb2.DeleteRequest(api_key=args.api_key or "", model_id=args.model_id)
        resp = stub.Delete(req)
        print(resp)
        return


if __name__ == "__main__":
    main()