# 사용 방법 (Usage Guide)

## 1. 개별 사이트 크롤링 (Crawling Individual Sites)
터미널에서 다음 명령어를 실행하여 특정 사이트의 최신 뉴스를 수집할 수 있습니다.

```bash
# Texas Tribune
scrapy crawl texas_tribune

# Dallas News
scrapy crawl dallas_news
```

## AI Configuration (Gemini vs Ollama)

LocuSum Ingestor supports both Google Gemini and Ollama for AI enrichment (Summarization & Embeddings).

### 1. Gemini (Default)
Ensure `GOOGLE_API_KEY` is set in `.env`.
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
```

### 2. Ollama
To use a local Ollama instance:
1.  Set `LLM_PROVIDER=ollama` in `.env`.
2.  Configure the URL and Model:
    ```bash
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    OLLAMA_MODEL=llama3
    ```
3.  **Important**: You must pull the models in Ollama first:
    ```bash
    ollama pull llama3
    ollama pull nomic-embed-text
    ```

# Community Impact
scrapy crawl community_impact

# Houston Chronicle (Playwright 필요)
scrapy crawl houston_chronicle

# Community Impact
scrapy crawl community_impact
```

## 1.1 일괄 크롤링 (Batch Crawling)
모든 크롤러를 순차적으로 실행하려면 다음 스크립트를 사용하세요.

```bash
# 실행 권한 부여 (최초 1회)
chmod +x run_crawlers.sh

# 일괄 실행
./run_crawlers.sh
```

## 2. 테스트 (Testing)
작성된 스파이더들의 파싱 로직을 검증하려면 다음 명령어를 실행합니다.

```bash
python3 -m unittest tests/test_spiders.py
```

## 3. 워커 실행 (Running Workers)
수집된 데이터를 처리하고 AI 요약을 수행하려면 다음 워커들을 실행해야 합니다.

### 3.1 데이터 처리 워커 (Ingestion Worker)
수집된 Raw Data(PostgreSQL `raw_articles` 테이블)를 정제하여 메인 테이블(`articles`)로 이동시킵니다.
> **Note:** 이제 SQLite를 사용하지 않고 바로 PostgreSQL을 사용합니다.
```bash
python3 -m locusum_ingestor.worker
```

### 3.2 AI 요약 워커 (AI Worker)
Google Gemini를 사용하여 기사 요약 및 임베딩을 생성합니다.
```bash
python3 -m locusum_ingestor.ai_worker
```
