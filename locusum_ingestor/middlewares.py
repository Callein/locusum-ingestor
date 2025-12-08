
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from sqlalchemy.orm import Session
from loguru import logger
from locusum_ingestor.models.main_db import engine, Article

class DuplicateCheckMiddleware:
    """
    Downloader Middleware to check if the URL already exists in the Main Database (Postgres).
    If it exists, the request is dropped (IgnoreRequest) to prevent re-downloading.
    """
    def __init__(self):
        # Create a new session factory or connection
        # It's better to open/close session per request or keep one open?
        # Keeping one open for the spider duration is okay for read-only checks, 
        # but Scrapy is async. SQLAlchemy Session is not thread-safe.
        # But Scrapy default is single-threaded (Twisted).
        self.session = Session(engine)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        # Skip check for robots.txt
        if "robots.txt" in request.url:
            return None

        try:
            # Check if URL exists in Postgres
            # We use distinct session or the one initialized? 
            # Given Scrapy's single thread loop, one session might be fine, 
            # but let's be safe and ensure rollback on error.
            
            # Optimization: Check exact match
            exists = self.session.query(Article.id).filter(Article.url == request.url).first()
            
            if exists:
                logger.debug(f"[DuplicateCheck] Found in Main DB. Ignoring: {request.url}")
                raise IgnoreRequest(f"Duplicate article in Main DB: {request.url}")
            
        except IgnoreRequest:
            raise
        except Exception as e:
            logger.error(f"Error in DuplicateCheckMiddleware: {e}")
            # If DB check fails, we probably should let it pass or fail safe?
            # Let's let it pass to ensure crawler doesn't break entirely if DB is momentary down,
            # though duplicates might occur.
            return None

        return None

    def spider_closed(self, spider):
        self.session.close()
