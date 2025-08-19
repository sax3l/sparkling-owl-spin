ENV?=dev

.PHONY: bootstrap up down types lint ci

bootstrap:
	@echo "--- Bootstrapping project ---"
	@echo "Pushing database schema..."
	supabase db push
	@echo "Deploying Supabase functions..."
	supabase functions deploy jobs_webhook
	supabase functions deploy retention
	supabase functions deploy erasure
	supabase functions deploy dq_recompute
	@echo "Installing frontend dependencies..."
	npm --prefix frontend install
	@echo "--- Bootstrap complete ---"

up:
	@echo "--- Starting services with Docker Compose ---"
	docker compose -f docker/docker-compose.yml up -d

down:
	@echo "--- Stopping services ---"
	docker compose -f docker/docker-compose.yml down

types:
	@echo "--- Generating TypeScript types from Supabase schema ---"
	supabase gen types typescript --linked > supabase/types/database-types.ts

lint:
	@echo "--- Running linters ---"
	ruff check src
	black --check src
	
ci:
	@echo "--- Running CI checks ---"
	make types
	pytest -q