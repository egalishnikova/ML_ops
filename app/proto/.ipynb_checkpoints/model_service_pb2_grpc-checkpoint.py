from __future__ import annotations
import grpc
from . import model_service_pb2 as model__service__pb2


class ModelServiceStub(object):
    def __init__(self, channel):
        self.Health = channel.unary_unary(
            "/modelservice.ModelService/Health",
            request_serializer=model__service__pb2.HealthRequest.SerializeToString,
            response_deserializer=model__service__pb2.HealthResponse.FromString,
        )
        self.ListModelClasses = channel.unary_unary(
            "/modelservice.ModelService/ListModelClasses",
            request_serializer=model__service__pb2.Empty.SerializeToString,
            response_deserializer=model__service__pb2.ModelClassesResponse.FromString,
        )
        self.ListModels = channel.unary_unary(
            "/modelservice.ModelService/ListModels",
            request_serializer=model__service__pb2.Empty.SerializeToString,
            response_deserializer=model__service__pb2.ListModelsResponse.FromString,
        )
        self.Train = channel.unary_unary(
            "/modelservice.ModelService/Train",
            request_serializer=model__service__pb2.TrainRequest.SerializeToString,
            response_deserializer=model__service__pb2.TrainResponse.FromString,
        )
        self.Predict = channel.unary_unary(
            "/modelservice.ModelService/Predict",
            request_serializer=model__service__pb2.PredictRequest.SerializeToString,
            response_deserializer=model__service__pb2.PredictResponse.FromString,
        )
        self.Retrain = channel.unary_unary(
            "/modelservice.ModelService/Retrain",
            request_serializer=model__service__pb2.RetrainRequest.SerializeToString,
            response_deserializer=model__service__pb2.TrainResponse.FromString,
        )
        self.Delete = channel.unary_unary(
            "/modelservice.ModelService/Delete",
            request_serializer=model__service__pb2.DeleteRequest.SerializeToString,
            response_deserializer=model__service__pb2.DeleteResponse.FromString,
        )


class ModelServiceServicer(object):
    def Health(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def ListModelClasses(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def ListModels(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Train(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Predict(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Retrain(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Delete(self, request, context):  # pragma: no cover
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ModelServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Health": grpc.unary_unary_rpc_method_handler(
            servicer.Health,
            request_deserializer=model__service__pb2.HealthRequest.FromString,
            response_serializer=model__service__pb2.HealthResponse.SerializeToString,
        ),
        "ListModelClasses": grpc.unary_unary_rpc_method_handler(
            servicer.ListModelClasses,
            request_deserializer=model__service__pb2.Empty.FromString,
            response_serializer=model__service__pb2.ModelClassesResponse.SerializeToString,
        ),
        "ListModels": grpc.unary_unary_rpc_method_handler(
            servicer.ListModels,
            request_deserializer=model__service__pb2.Empty.FromString,
            response_serializer=model__service__pb2.ListModelsResponse.SerializeToString,
        ),
        "Train": grpc.unary_unary_rpc_method_handler(
            servicer.Train,
            request_deserializer=model__service__pb2.TrainRequest.FromString,
            response_serializer=model__service__pb2.TrainResponse.SerializeToString,
        ),
        "Predict": grpc.unary_unary_rpc_method_handler(
            servicer.Predict,
            request_deserializer=model__service__pb2.PredictRequest.FromString,
            response_serializer=model__service__pb2.PredictResponse.SerializeToString,
        ),
        "Retrain": grpc.unary_unary_rpc_method_handler(
            servicer.Retrain,
            request_deserializer=model__service__pb2.RetrainRequest.FromString,
            response_serializer=model__service__pb2.TrainResponse.SerializeToString,
        ),
        "Delete": grpc.unary_unary_rpc_method_handler(
            servicer.Delete,
            request_deserializer=model__service__pb2.DeleteRequest.FromString,
            response_serializer=model__service__pb2.DeleteResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "modelservice.ModelService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))