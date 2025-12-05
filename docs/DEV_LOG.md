# Development Log - Locusum Ingestor

이 문서는 `locusum_ingestor` 모듈의 초기 구축부터 리팩토링, 테스트 작성까지의 작업 내역을 기록합니다.

## 1. 초기 구축 (Initial Setup)
`TASK_01_ingestor_setup.md` 명세서를 바탕으로 다음 기능을 구현했습니다.
- **Scrapy + Playwright**: 동적 웹 페이지 크롤링 지원.
- **SQLite + SQLModel**: 수집된 데이터를 저장할 로컬 버퍼 DB 구축.
- **Deduplication**: URL SHA-256 해시를 이용한 중복 수집 방지 로직 구현.

## 2. 리팩토링 (Refactoring)
초기 구현 후, 프로젝트 구조를 시니어 레벨의 Python 패키지 구조로 개선했습니다.
- **패키지화**: 모든 소스 코드를 `locusum_ingestor/` 패키지 내부로 이동.
- **정리**: 레거시 파일(`locu_sum_crawler_mvp_python.py`, `requirements.txt ` 등) 삭제.
- **설정 분리**: `scrapy.cfg`, `pyproject.toml` 등을 통해 프로젝트 설정 관리.

## 3. 문서화 (Documentation)
`docs/` 디렉토리에 프로젝트 이해를 돕는 문서를 작성했습니다.
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: 시스템 아키텍처, 데이터 모델, 향후 로드맵 기술.
- **[TESTING.md](TESTING.md)**: 테스트 실행 방법 및 구조 설명 (한국어).

## 4. 테스트 (Testing)
`pytest`를 도입하여 핵심 로직을 검증하는 테스트 코드를 작성했습니다.
- **DB 테스트**: `RawArticle` 모델의 CRUD 및 제약조건 테스트.
- **파이프라인 테스트**: 중복 제거 로직 검증.
- **In-Memory DB**: `conftest.py`를 통해 테스트 격리 환경 구성.

## 5. 실행 방법 (How to Run)

### 의존성 설치
```bash
pip install scrapy scrapy-playwright sqlmodel loguru playwright pytest pytest-asyncio
playwright install
```

### 크롤러 실행
```bash
python -m locusum_ingestor.main "https://news.ycombinator.com" "title=span.titleline > a"
```

### 테스트 실행
```bash
PYTHONPATH=. pytest
```
