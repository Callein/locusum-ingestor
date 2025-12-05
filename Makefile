# Makefile for locusum_ingestor

.PHONY: up down crawl enrich test lint

up:
	docker compose -f deploy/docker-compose.yml up -d

down:
	docker compose -f deploy/docker-compose.yml down -v

crawl-once:
	curl -X POST http://localhost:9010/admin/trigger

enrich-once:
	curl -X POST http://localhost:9020/admin/trigger

test:
	pytest -q

lint:
	ruff check .
	black . --check
	mypy . --ignore-missing-imports