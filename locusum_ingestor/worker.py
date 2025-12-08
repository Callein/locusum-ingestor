
import time
import sys
import os
from sqlalchemy.orm import Session
from loguru import logger

from locusum_ingestor.database import get_session as get_sqlite_session, RawArticle
from locusum_ingestor.models.main_db import get_session as get_pg_session, Article, create_db_and_tables
from locusum_ingestor.processor.extractor import extract_content

def run_worker():
    """
    Main ETL loop:
    1. Fetch 'NEW' articles from SQLite.
    2. Extract content.
    3. Save to Postgres.
    4. Mark as 'PROCESSED'.
    """
    logger.info("Starting Locusum Processor Worker...")
    
    # Ensure Postgres tables exist with retry logic
    retries = 5
    while retries > 0:
        try:
            create_db_and_tables()
            logger.info("Main DB tables verified.")
            break
        except Exception as e:
            logger.warning(f"Failed to connect/create tables in Main DB: {e}. Retrying in 5s...")
            time.sleep(5)
            retries -= 1
    
    if retries == 0:
        logger.error("Could not connect to Main DB after retries. Exiting.")
        return

    sqlite_session = get_sqlite_session()
    pg_session = get_pg_session()

    while True:
        try:
            # Fetch batch of 10
            raw_articles = sqlite_session.query(RawArticle).filter(RawArticle.status == "NEW").limit(10).all()
            
            if not raw_articles:
                logger.info("No new articles. Sleeping for 10s...")
                time.sleep(10)
                continue
            
            logger.info(f"Processing batch of {len(raw_articles)} articles...")
            
            for raw in raw_articles:
                try:
                    # 1. Extract content
                    clean_text = extract_content(raw.html_content)
                    
                    if not clean_text:
                        logger.warning(f"Empty content for {raw.url}. Marking as FAILED.")
                        raw.status = "FAILED_EMPTY"
                        sqlite_session.commit()
                        continue

                    # 2. Create Postgres Article
                    # Check for duplicate in PG based on URL (optional but good practice)
                    existing_pg = pg_session.query(Article).filter(Article.url == raw.url).first()
                    if existing_pg:
                         logger.info(f"Article already exists in PG: {raw.url}. Marking processed.")
                    else:
                        new_article = Article(
                            raw_id=raw.id,
                            url=raw.url,
                            source=raw.source,
                            title=raw.title,
                            content=clean_text,
                            published_at=raw.fetched_at # Approximate
                        )
                        pg_session.add(new_article)
                        pg_session.commit()
                        logger.info(f"Saved to PG: {raw.title[:30]}...")

                    # 3. Cleanup from SQLite (Buffer)
                    logger.debug(f"Removing from SQLite buffer: {raw.url}")
                    sqlite_session.delete(raw)
                    sqlite_session.commit()

                except Exception as e:
                    logger.error(f"Error processing article {raw.id}: {e}")
                    sqlite_session.rollback()
                    pg_session.rollback()
                    # Mark as error to avoid infinite loop
                    raw.status = "ERROR"
                    sqlite_session.commit()
            
        except KeyboardInterrupt:
            logger.info("Worker calling it a day.")
            break
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker()
