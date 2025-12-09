# 사용 방법 (Usage Guide)

## 1. 개별 사이트 크롤링 (Crawling Individual Sites)
터미널에서 다음 명령어를 실행하여 특정 사이트의 최신 뉴스를 수집할 수 있습니다.

```bash
# Texas Tribune
scrapy crawl texas_tribune

# Dallas News
scrapy crawl dallas_news

# Houston Chronicle (Playwright 필요)
scrapy crawl houston_chronicle

# Community Impact
scrapy crawl community_impact
```

## 2. 테스트 (Testing)
작성된 스파이더들의 파싱 로직을 검증하려면 다음 명령어를 실행합니다.

```bash
python3 -m unittest tests/test_spiders.py
```

## 3. 워커 실행 (Running Workers)
수집된 데이터를 처리하고 AI 요약을 수행하려면 다음 워커들을 실행해야 합니다.

### 3.1 데이터 처리 워커 (Ingestion Worker)
SQLite 버퍼에서 PostgreSQL로 데이터를 이동시킵니다.
```bash
python3 -m locusum_ingestor.worker
```

### 3.2 AI 요약 워커 (AI Worker)
Google Gemini를 사용하여 기사 요약 및 임베딩을 생성합니다.
```bash
python3 -m locusum_ingestor.ai_worker
```
