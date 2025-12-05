import hashlib
import pytest
from scrapy.exceptions import DropItem
from locusum_ingestor.pipelines import LocusumIngestorPipeline
from locusum_ingestor.database import RawArticle

class MockSpider:
    pass

def test_pipeline_process_item(session):
    # Override pipeline session with test session
    pipeline = LocusumIngestorPipeline()
    pipeline.session = session # Inject test session

    item = {
        "url": "https://example.com/pipeline-test",
        "source": "Pipeline Source",
        "title": "Pipeline Title",
        "html_content": "<html>Pipeline</html>"
    }

    # First run: Should save
    processed_item = pipeline.process_item(item, MockSpider())
    assert processed_item == item
    
    # Verify in DB
    url_hash = hashlib.sha256(item["url"].encode("utf-8")).hexdigest()
    saved_article = session.get(RawArticle, url_hash)
    assert saved_article is not None
    assert saved_article.url == item["url"]

    # Second run: Should drop (Duplicate)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, MockSpider())
    
    assert "Duplicate item found" in str(excinfo.value)
