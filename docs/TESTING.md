# 테스트 가이드 - Locusum Ingestor

이 문서는 Locusum Ingestor 프로젝트의 테스트를 실행하고 작성하는 방법에 대해 설명합니다.

## 1. 사전 요구 사항 (Prerequisites)

개발 의존성 패키지가 설치되어 있는지 확인하세요. 아직 설치하지 않았다면 다음 명령어를 실행하세요:

```bash
pip install pytest pytest-asyncio
```

## 2. 테스트 실행 (Running Tests)

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 전체 테스트 스위트를 실행할 수 있습니다:

```bash
PYTHONPATH=. pytest
```

### 주요 옵션
- **상세 출력 (Verbose)**: `PYTHONPATH=. pytest -v`
- **특정 테스트 파일 실행**: `PYTHONPATH=. pytest tests/test_database.py`
- **특정 테스트 케이스 실행**: `PYTHONPATH=. pytest tests/test_database.py::test_create_raw_article`

## 3. 테스트 구조 (Test Structure)

테스트 코드는 `tests/` 디렉토리에 위치합니다:

```
tests/
├── conftest.py         # 공통 픽스처 (예: In-memory DB 세션)
├── test_database.py    # SQLModel 데이터베이스 상호작용 테스트
└── test_pipeline.py    # Scrapy 파이프라인 로직 테스트 (중복 제거 등)
```

### 주요 구성 요소

#### `conftest.py`
`session` 픽스처를 정의합니다. 이 픽스처는 각 테스트 함수마다 격리된 **In-Memory SQLite** 데이터베이스 세션을 제공합니다. 이를 통해 테스트가 실제 파일 기반 데이터베이스(`locusum_buffer.db`)에 영향을 주지 않고 독립적으로 실행될 수 있도록 보장합니다.

#### `test_database.py`
`RawArticle` 데이터 모델의 무결성을 검증합니다:
- 레코드 생성 및 조회.
- 유니크 제약 조건(예: URL 중복 방지) 강제 여부 확인.

#### `test_pipeline.py`
`LocusumIngestorPipeline`을 테스트합니다:
- **아이템 처리 (Process Item)**: 새로운 아이템이 DB에 올바르게 저장되는지 확인합니다.
- **중복 제거 (Deduplication)**: 중복된 아이템(동일한 URL 해시)이 들어왔을 때 `DropItem` 예외가 발생하고 저장되지 않는지 확인합니다.

## 4. 새로운 테스트 작성하기 (Writing New Tests)

1.  `tests/` 디렉토리에 `test_`로 시작하는 새로운 파이썬 파일을 생성합니다.
2.  데이터베이스 접근이 필요하다면 `conftest.py`의 `session` 픽스처를 인자로 받습니다.
3.  `test_`로 시작하는 테스트 함수를 작성합니다.

예시:
```python
def test_example(session):
    # 테스트 로직 작성
    assert True
```

## 5. 지속적 통합 (CI)

CI(예: GitHub Actions)를 구성할 때 다음 단계가 포함되어야 합니다:
1.  코드 체크아웃 (Checkout code).
2.  Python 및 의존성 설치.
3.  Playwright 브라우저 설치 (`playwright install`).
4.  테스트 실행 (`PYTHONPATH=. pytest`).
