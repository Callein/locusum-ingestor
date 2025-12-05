import hashlib
from sqlalchemy.orm import Session
from scrapy.exceptions import DropItem
from loguru import logger
from locusum_ingestor.database import engine, RawArticle

class LocusumIngestorPipeline:
    def __init__(self):
        self.session = Session(engine)

    def process_item(self, item, spider):
        url = item.get("url")
        if not url:
            raise DropItem("Missing URL in item")

        # 1. Calculate SHA-256 hash of the URL
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()

        # 2. Check if exists in DB
        existing = self.session.get(RawArticle, url_hash)
        if existing:
            logger.info(f"Duplicate found: {url} (ID: {url_hash}). Skipping.")
            raise DropItem(f"Duplicate item found: {url}")

        # 3. Save to SQLite
        new_article = RawArticle(
            id=url_hash,
            url=url,
            source=item.get("source", "Unknown"),
            title=item.get("title"),
            html_content=item.get("html_content"),
            status="NEW"
        )
        
        try:
            self.session.add(new_article)
            self.session.commit()
            logger.info(f"Saved new article: {url} (ID: {url_hash})")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save article {url}: {e}")
            raise DropItem(f"Database error: {e}")

        return item

    def close_spider(self, spider):
        self.session.close()
