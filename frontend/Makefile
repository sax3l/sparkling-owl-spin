# ECaDP - Ethical Crawler & Data Platform
# Makefile för utveckling och drift

.PHONY: help up down test lint e2e seed gen-sdk docs clean install-dev

# Standard mål
help: ## Visa hjälp
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Utvecklingsmiljö
up: ## Starta utvecklingsmiljö (Docker Compose)
	docker-compose -f docker/docker-compose.dev.yml up -d
	@echo "🚀 Utvecklingsmiljö startad på http://localhost:8000"
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📈 Prometheus: http://localhost:9090"

down: ## Stoppa utvecklingsmiljö
	docker-compose -f docker/docker-compose.dev.yml down
	docker-compose -f docker/docker-compose.synthetic.yml down

restart: down up ## Restart utvecklingsmiljö

# Databas
init: ## Initiera databas och migrationer
	python scripts/init_db.py
	@echo "✅ Databas initierad"

seed: ## Ladda seed-data
	python scripts/seed_data.py
	@echo "✅ Seed-data laddad"

# Tester
test: ## Kör unit tests
	pytest tests/unit/ -v --cov=src --cov-report=html
	@echo "✅ Unit tests slutförda"

integration: ## Kör integration tests
	pytest tests/integration/ -v
	@echo "✅ Integration tests slutförda"

e2e: ## Kör end-to-end tests
	docker-compose -f docker/docker-compose.synthetic.yml up -d
	sleep 10
	pytest tests/e2e/ -v
	docker-compose -f docker/docker-compose.synthetic.yml down
	@echo "✅ E2E tests slutförda"

test-all: test integration e2e ## Kör alla tester

# Kvalitetsgranskning
lint: ## Kör linting (ruff, mypy, black)
	ruff check src/ --fix
	black src/
	isort src/
	mypy src/
	@echo "✅ Linting slutfört"

security: ## Kör säkerhetsscanning
	bandit -r src/
	safety check
	@echo "✅ Säkerhetsscanning slutförd"

format: ## Formatera kod
	black src/
	isort src/
	@echo "✅ Kod formaterad"

# SDK och dokumentation
gen-sdk: ## Generera SDK:er
	./scripts/generate_sdk.sh
	@echo "✅ SDK:er genererade"

docs: ## Generera dokumentation
	cd docs && mkdocs build
	@echo "✅ Dokumentation byggd i docs/site/"

docs-serve: ## Servera dokumentation lokalt
	cd docs && mkdocs serve
	@echo "📚 Dokumentation: http://localhost:8080"

# Drift och underhåll
backup: ## Kör manuell backup
	./scripts/backup_now.sh
	@echo "✅ Backup slutförd"

restore-drill: ## Kör restore-övning
	./scripts/restore_drill.sh
	@echo "✅ Restore-övning slutförd"

sync-s3: ## Synka data till S3
	./scripts/s3_sync.sh
	@echo "✅ S3-synkronisering slutförd"

# Crawler och scraper
crawl: ## Starta crawler manuellt
	python scripts/run_crawler.py
	@echo "🕷️ Crawler startad"

scrape: ## Starta scraper manuellt
	python scripts/run_scraper.py
	@echo "🔍 Scraper startad"

scheduler: ## Starta scheduler
	python scripts/start_scheduler.py
	@echo "⏰ Scheduler startad"

analysis: ## Kör dataanalys
	python scripts/run_analysis.py
	@echo "📊 Analys slutförd"

diagnose: ## Kör diagnostikverktyg
	python scripts/diagnostic_tool.py
	@echo "🔧 Diagnostik slutförd"

# Installation och setup
install-dev: ## Installera utvecklingsdependencies
	pip install -e .
	pip install -r requirements-dev.txt
	npm install
	@echo "✅ Utvecklingsdependencies installerade"

install: ## Installera produktionsdependencies
	pip install -r requirements.txt
	@echo "✅ Produktionsdependencies installerade"

# Rengöring
clean: ## Rensa temporära filer
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "🧹 Temporära filer rensade"

clean-data: ## Rensa lokal data (VARNING: raderar all data!)
	rm -rf data/raw/*
	rm -rf data/processed/*
	rm -rf data/exports/*
	@echo "⚠️ Lokal data rensad"

# Docker builds
build-app: ## Bygg app-container
	docker build -f docker/Dockerfile.app -t ecadp-app .

build-worker: ## Bygg worker-container
	docker build -f docker/Dockerfile.worker -t ecadp-worker .

build-browser: ## Bygg browser-container
	docker build -f docker/Dockerfile.browser -t ecadp-browser .

build-all: build-app build-worker build-browser ## Bygg alla containers

# Kubernetes
k8s-apply: ## Appliera K8s manifests
	kubectl apply -k iac/k8s/

k8s-delete: ## Ta bort K8s resources
	kubectl delete -k iac/k8s/

# Monitoring
logs-app: ## Visa app-loggar
	docker-compose -f docker/docker-compose.dev.yml logs -f app

logs-worker: ## Visa worker-loggar
	docker-compose -f docker/docker-compose.dev.yml logs -f worker

logs-all: ## Visa alla loggar
	docker-compose -f docker/docker-compose.dev.yml logs -f

# Utvecklingshjälp
shell-app: ## Öppna shell i app-container
	docker-compose -f docker/docker-compose.dev.yml exec app bash

shell-worker: ## Öppna shell i worker-container
	docker-compose -f docker/docker-compose.dev.yml exec worker bash

# Frontend
frontend-dev: ## Starta frontend i dev-läge
	cd frontend && npm run dev

frontend-build: ## Bygg frontend för produktion
	cd frontend && npm run build

frontend-test: ## Testa frontend
	cd frontend && npm test

# Performance
benchmark: ## Kör performance benchmarks
	python -m pytest tests/performance/ -v
	@echo "⚡ Performance benchmarks slutförda"

# Default mål
.DEFAULT_GOAL := help