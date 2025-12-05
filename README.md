# locusum_ingestor

A minimal MVP pipeline that crawls RSS feeds, extracts article text, stores raw articles in SQLite, enriches them with embeddings, keywords and stores results in PostgreSQL (pgvector + full‑text search).

## Services
- **crawler** – reads RSS feeds, respects `robots.txt`, extracts main text with `trafilatura`, upserts into `crawler.db`.
- **enricher** – reads new rows, calls an external embedding service (`/embed`), extracts keywords/entities, builds a tsvector and upserts into Postgres.

Both services expose FastAPI admin endpoints (`/health`, `/admin/trigger`).

## Quickstart
1. Copy example env files and adjust values:
   ```bash
   cp deploy/env/*.example.env .
   ```
2. Start the stack:
   ```bash
   make up
   ```
3. Trigger a crawl and enrichment run:
   ```bash
   make crawl-once   # POST /admin/trigger to crawler
   make enrich-once  # POST /admin/trigger to enricher
   ```
4. Connect to Postgres (`localhost:5432`) and query the `articles` table.

## Requirements
- Python 3.11+
- Docker & Docker Compose (pgvector image)
- External embedding service reachable via `EMB_URL`

See the `README.md` in each service for more details.