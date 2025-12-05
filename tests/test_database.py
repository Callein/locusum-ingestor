from locusum_ingestor.database import RawArticle
import datetime

def test_create_raw_article(session):
    article = RawArticle(
        id="test_hash_123",
        url="https://example.com/news/1",
        source="Test Source",
        title="Test Title",
        html_content="<html><body>Test</body></html>",
        status="NEW"
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    assert article.id == "test_hash_123"
    assert article.url == "https://example.com/news/1"
    assert article.status == "NEW"
    assert isinstance(article.fetched_at, datetime.datetime)

def test_unique_url_constraint(session):
    article1 = RawArticle(
        id="hash1",
        url="https://example.com/unique",
        source="Source 1",
        html_content="content",
        status="NEW"
    )
    session.add(article1)
    session.commit()

    # Try inserting same URL with different ID (should fail due to unique constraint on URL)
    # Note: In our logic ID is hash of URL, so usually ID would clash too, 
    # but here we test the DB constraint specifically.
    article2 = RawArticle(
        id="hash2",
        url="https://example.com/unique", 
        source="Source 2",
        html_content="content",
        status="NEW"
    )
    session.add(article2)
    
    from sqlalchemy.exc import IntegrityError
    import pytest
    
    with pytest.raises(IntegrityError):
        session.commit()
