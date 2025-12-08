# 크롤링 정책 및 구현 상세 (Crawling Policy)

본 문서는 `locusum-ingestor` 모듈의 뉴스 크롤링 정책 및 기술 구현 사항을 설명합니다.

## 1. 수집 대상 사이트 (Target Sites)

| 사이트 명 | URL | 수집 방식 | 비고 |
| :--- | :--- | :--- | :--- |
| **Texas Tribune** | [texastribune.org](https://www.texastribune.org/) | Standard Scrapy | 일반적인 HTML 구조, `h2`, `h3` 태그에서 기사 링크 추출 |
| **Dallas News** | [dallasnews.com](https://www.dallasnews.com/) | Standard Scrapy | URL 패턴 기반 추출 (`/YYYY/MM/DD/`) |
| **Houston Chronicle** | [houstonchronicle.com](https://www.houstonchronicle.com/) | **Scrapy + Playwright** | Paywall/Bot 차단 우회를 위해 Headless Browser 사용 |
| **Community Impact** | [communityimpact.com](https://communityimpact.com/) | Standard Scrapy | URL 패턴 기반 추출 (`/YYYY/MM/DD/`) |

## 2. 기술 구현 (Technical Implementation)

### 2.1 스파이더 (Spiders)
- **위치**: `locusum_ingestor/spiders/`
- 각 사이트별로 별도의 Spider 클래스로 구현되어 독립적으로 유지보수가 가능합니다.
- **Houston Chronicle**의 경우 `scrapy-playwright` 미들웨어를 사용하여 자바스크립트 렌더링 및 차단 우회를 처리합니다.

### 2.2 데이터 저장 (Storage)
- **데이터베이스**: SQLite (`locusum_buffer.db`)
- **테이블**: `raw_articles`
- **중복 처리**: 
    - 기사 URL의 **SHA-256 해시**를 Primary Key(`id`)로 사용합니다.
    - 이미 존재하는 해시값의 기사가 수집되면 `DropItem` 예외를 발생시켜 중복 저장을 방지합니다. (`pipelines.py`)
- **저장 항목**:
    - `id`: URL 해시 (PK)
    - `url`: 원본 기사 링크
    - `source`: 언론사 명
    - `title`: 기사 제목
    - `html_content`: 기사 본문 HTML (Raw)
    - `fetched_at`: 수집 시각
    - `status`: 상태 (기본값 'NEW')

## 3. 실행 방법 (Usage)

### 3.1 개별 사이트 크롤링
터미널에서 다음 명령어를 실행하여 특정 사이트를 수집할 수 있습니다.

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

### 3.2 테스트 (Testing)
작성된 스파이더들의 파싱 로직을 검증하려면 다음 명령어를 실행합니다.

```bash
python3 -m unittest tests/test_spiders.py
```

## 4. 수집 기간 및 범위 (Crawling Period & Scope)

현재 구현된 스크래퍼들은 **"최신 뉴스(Latest News)"** 수집을 목적으로 설계되었습니다.

- **수집 시작점**: 각 뉴스 사이트의 **메인 홈페이지(Homepage)**
- **수집 범위**: 홈페이지에 노출된 기사 링크 중, 기사 패턴(예: `/YYYY/MM/DD/`)과 일치하는 항목을 수집합니다.
- **기간 정책**:
    - 별도의 과거 날짜 필터링(History Backfill) 로직은 포함되어 있지 않습니다.
    - 스크래퍼가 실행되는 시점에 메인 페이지에 걸려 있는 **가장 최신 기사**들이 수집 대상이 됩니다.
    - 정기적(예: 매일/매시간)으로 스크래퍼를 실행하여 지속적으로 최신 기사를 누적하는 방식(Running Forward)을 따릅니다.
