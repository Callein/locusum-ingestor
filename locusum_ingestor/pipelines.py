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

        # 2. Check if exists in DB & 3. Save to SQLite
        try:
            # Check for duplicate
            existing = self.session.get(RawArticle, url_hash)
            if existing:
                logger.info(f"Duplicate found: {url} (ID: {url_hash}). Skipping.")
                raise DropItem(f"Duplicate item found: {url}")

            # Save new article
            new_article = RawArticle(
                id=url_hash,
                url=url,
                source=item.get("source", "Unknown"),
                region=item.get("region"),
                author=item.get("author"),
                image_url=item.get("image_url"),
                title=item.get("title"),
                html_content=item.get("html_content"),
                status="NEW"
            )
            
            self.session.add(new_article)
            self.session.commit()
            logger.info(f"Saved new article: {url} (ID: {url_hash})")

        except DropItem:
            # Re-raise DropItem as it's a normal Scrapy flow control
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Database error processing {url}: {e}")
            raise DropItem(f"Database error: {e}")

        return item

    def close_spider(self, spider):
        self.session.close()
