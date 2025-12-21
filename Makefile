SHELL := /bin/bash

IMAGE_NAME ?= ml_ops
TAG ?= latest
DOCKERHUB_USER ?= your_dockerhub_login

.PHONY: docker-build-push test lint

docker-build-push:
	@echo "Building image..."
	docker build -t $(DOCKERHUB_USER)/$(IMAGE_NAME):$(TAG) .
	@echo "Pushing image..."
	docker push $(DOCKERHUB_USER)/$(IMAGE_NAME):$(TAG)

test:
	poetry run pytest -q

lint:
	poetry run ruff check .
