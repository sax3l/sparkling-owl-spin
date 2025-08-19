.PHONY: help install-dev test lint run-api docker-up docker-down clean

help:
	@echo "Commands:"
	@echo "  install-dev      : Install development dependencies"
	@echo "  test             : Run all tests"
	@echo "  test-unit        : Run unit tests"
	@echo "  test-integration : Run integration tests"
	@echo "  test-e2e         : Run end-to-end tests"
	@echo "  lint             : Run linters and formatters"
	@echo "  run-api          : Run the FastAPI web application"
	@echo "  docker-up        : Start synthetic services with Docker Compose"
	@echo "  docker-down      : Stop synthetic services"
	@echo "  clean            : Clean up build artifacts"

install-dev:
	pip install -r requirements.txt
	pip install -r requirements_dev.txt

test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-e2e:
	pytest -m e2e

lint:
	ruff check .
	black .
	mypy src

run-api:
	uvicorn src.webapp.app:app --reload

docker-up:
	docker-compose -f docker/docker-compose.synthetic.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.synthetic.yml down

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache .coverage htmlcov