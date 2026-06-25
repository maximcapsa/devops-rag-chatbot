.PHONY: help install dev ingest run lint test docker-build docker-run tf-init tf-plan tf-apply

help:
	@echo "Targets:"
	@echo "  install      Install runtime deps"
	@echo "  dev          Install dev deps"
	@echo "  ingest       Build the FAISS index from data/"
	@echo "  run          Run the API locally (uvicorn, reload)"
	@echo "  lint         Run ruff"
	@echo "  test         Run pytest"
	@echo "  docker-build Build the Docker image"
	@echo "  docker-run   Run via docker compose"
	@echo "  tf-plan      Terraform plan (in terraform/)"
	@echo "  tf-apply     Terraform apply (in terraform/)"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

ingest:
	python -m app.ingest

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .

test:
	pytest

docker-build:
	docker build -t devops-rag:local .

docker-run:
	docker compose up --build

tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply
