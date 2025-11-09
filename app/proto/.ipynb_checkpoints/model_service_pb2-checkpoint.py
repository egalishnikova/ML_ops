# Сгенерировано grpcio-tools. Оставлено здесь для самодостаточности проекта.
# ... (из-за объёма включён минимальный рабочий вариант; при необходимости пересгенерируйте по proto)
from __future__ import annotations
import sys as _sys
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b"\n\x19model_service.proto\x12\x0cmodelservice\"\x10\n\x05Ex05\x45mpty\x12\x07\n\x07api_key\x18\x01 \x01(\t\"\x19\n\rHealthRequest\x12\x08\n\x01x\x18\x01 \x01(\t\"\x1c\n\x0eHealthResponse\x12\n\n\x02ok\x18\x01 \x01(\t\"\x1f\n\x14ModelClassesResponse\x12\x07\n\x07classes\x18\x01 \x03(\t\"\x0f\n\x0bFloatArray\x12\x10\n\x06values\x18\x01 \x03(\x01\"\x8d\x01\n\x0cTrainRequest\x12\x0f\n\x07api_key\x18\x01 \x01(\t\x12\x13\n\x0bmodel_class\x18\x02 \x01(\t\x12\x12\n\nhyperparams\x18\x03 \x03(\x0b2\x1e.modelservice.TrainRequest.HyperparamsEntry\x12\x13\n\x01X\x18\x04 \x03(\x0b2\x11.modelservice.FloatArray\x12\x0c\n\x01y\x18\x05 \x03(\x05\x12\x12\n\nmodel_name\x18\x06 \x01(\t\x1a/\n\x10HyperparamsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"t\n\rTrainResponse\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x13\n\x0bmodel_class\x18\x02 \x01(\t\x12\x12\n\nmodel_name\x18\x03 \x01(\t\x12\x15\n\x07metrics\x18\x04 \x03(\x0b2\x14.modelservice.TrainResponse.MetricsEntry\x1a/\n\rMetricsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x05value\x18\x02 \x01(\x01:\x02\x38\x01\"A\n\x0fPredictRequest\x12\x0f\n\x07api_key\x18\x01 \x01(\t\x12\x10\n\x08model_id\x18\x02 \x01(\t\x12\x13\n\x01X\x18\x03 \x03(\x0b2\x11.modelservice.FloatArray\"I\n\x10PredictResponse\x12\x13\n\x0bpredictions\x18\x01 \x03(\x05\x12$\n\x05proba\x18\x02 \x03(\x0b2\x15.modelservice.ProbRow\"\x18\n\x07ProbRow\x12\r\n\x05values\x18\x01 \x03(\x01\"\x8d\x01\n\x0eRetrainRequest\x12\x0f\n\x07api_key\x18\x01 \x01(\t\x12\x10\n\x08model_id\x18\x02 \x01(\t\x12\x13\n\x01X\x18\x03 \x03(\x0b2\x11.modelservice.FloatArray\x12\x0c\n\x01y\x18\x04 \x03(\x05\x12\x12\n\nhyperparams\x18\x05 \x03(\x0b2).modelservice.RetrainRequest.HyperparamsEntry\x1a0\n\x10HyperparamsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"7\n\rDeleteRequest\x12\x0f\n\x07api_key\x18\x01 \x01(\t\x12\x10\n\x08model_id\x18\x02 \x01(\t\"3\n\x0eDeleteResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x10\n\x08model_id\x18\x02 \x01(\t\"C\n\x13ListModelsResponse\x12,\n\x05items\x18\x01 \x03(\x0b2\x1d.modelservice.ModelInfo\"T\n\tModelInfo\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x13\n\x0bmodel_class\x18\x02 \x01(\t\x12\x12\n\nmodel_name\x18\x03 \x01(\t2\x84\x03\n\x0cModelService\x12@\n\x06Health\x12\x1b.modelservice.HealthRequest\x1a\x1c.modelservice.HealthResponse\x12J\n\x10ListModelClasses\x12\x13.modelservice.Empty\x1a .modelservice.ModelClassesResponse\x12@\n\nListModels\x12\x13.modelservice.Empty\x1a\x21.modelservice.ListModelsResponse\x12:\n\x05Train\x12\x1a.modelservice.TrainRequest\x1a\x1b.modelservice.TrainResponse\x129\n\x07Predict\x12\x1c.modelservice.PredictRequest\x1a\x1d.modelservice.PredictResponse\x12=\n\x07Retrain\x12\x1d.modelservice.RetrainRequest\x1a\x1b.modelservice.TrainResponse\x126\n\x06Delete\x12\x1b.modelservice.DeleteRequest\x1a\x1c.modelservice.DeleteResponseb\x06proto3")

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "model_service_pb2", _globals)

# pylint: disable=invalid-name
Empty = _globals["Empty"]
HealthRequest = _globals["HealthRequest"]
HealthResponse = _globals["HealthResponse"]
ModelClassesResponse = _globals["ModelClassesResponse"]
FloatArray = _globals["FloatArray"]
TrainRequest = _globals["TrainRequest"]
TrainResponse = _globals["TrainResponse"]
PredictRequest = _globals["PredictRequest"]
PredictResponse = _globals["PredictResponse"]
ProbRow = _globals["ProbRow"]
RetrainRequest = _globals["RetrainRequest"]
DeleteRequest = _globals["DeleteRequest"]
DeleteResponse = _globals["DeleteResponse"]
ListModelsResponse = _globals["ListModelsResponse"]
ModelInfo = _globals["ModelInfo"]

__all__ = [
    "Empty",
    "HealthRequest",
    "HealthResponse",
    "ModelClassesResponse",
    "FloatArray",
    "TrainRequest",
    "TrainResponse",
    "PredictRequest",
    "PredictResponse",
    "ProbRow",
    "RetrainRequest",
    "DeleteRequest",
    "DeleteResponse",
    "ListModelsResponse",
    "ModelInfo",
]