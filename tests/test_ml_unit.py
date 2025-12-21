from app.ml.trainer import predict, train_model


def test_train_and_predict_logreg_unit():
    X = [[0, 0], [1, 1], [1, 0], [0, 1]]
    y = [0, 1, 1, 0]

    model, metrics = train_model("logreg", {"max_iter": 200}, X, y)
    assert "train_accuracy" in metrics
    assert 0.0 <= float(metrics["train_accuracy"]) <= 1.0

    preds, proba = predict(model, [[1, 1], [0, 0]])
    assert len(preds) == 2
    assert len(proba) == 2
