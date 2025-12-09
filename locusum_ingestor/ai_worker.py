
import time
import sys
import os
from sqlalchemy import text
from loguru import logger
from locusum_ingestor.models.main_db import get_session, Article
from locusum_ingestor.services.ai_service import AIService
from sqlmodel import select

def run_ai_worker():
    """
    AI Enrichment Worker:
    1. Fetch articles where summary IS NULL (limit 10).
    2. Generate Summary & Embedding via AIService.
    3. Update DB.
    """
    logger.info("Starting Locusum AI Worker (Gemini)...")
    
    try:
        ai_service = AIService()
        logger.info("AIService initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize AIService: {e}")
        return

    session = get_session()
    idle_count = 0
    MAX_IDLE_RETRIES = 3

    while True:
        try:
            # Fetch batch of 10 articles that need processing
            # Using raw SQL filter for NULL check or SQLModel expression
            statement = select(Article).where(Article.summary == None).limit(10)
            articles = session.exec(statement).all()
            
            if not articles:
                idle_count += 1
                if idle_count >= MAX_IDLE_RETRIES:
                    logger.info(f"No articles to enrich for {MAX_IDLE_RETRIES} consecutive checks. AI Worker exiting gracefully.")
                    break
                
                logger.info(f"No articles to enrich (Idle {idle_count}/{MAX_IDLE_RETRIES}). Sleeping for 10s...")
                time.sleep(10)
                continue
            
            # Reset idle count
            idle_count = 0
            
            logger.info(f"Enriching batch of {len(articles)} articles...")
            
            for article in articles:
                try:
                    # 1. Summarize
                    if not article.content:
                        logger.warning(f"Skipping empty content article ID {article.id}")
                        continue
                        
                    summary = ai_service.summarize(article.content)
                    if not summary:
                        logger.warning(f"Summary generation failed for ID {article.id}")
                        # Mark as processed or failed? avoiding infinite loop is hard without status.
                        # For now, let's set a placeholder or specific retry logic.
                        # Setting placeholder to avoid re-fetch loop for now.
                        summary = "(Summary Failed)"

                    # 2. Embed
                    embedding = ai_service.embed(article.content)
                    if not embedding:
                        logger.warning(f"Embedding generation failed for ID {article.id}")
                    
                    # 3. Update DB
                    article.summary = summary
                    article.embedding = embedding
                    
                    session.add(article)
                    session.commit()
                    logger.info(f"Enriched Article ID {article.id}: {article.title[:20]}...")

                    # Rate limit respect for Free Tier
                    time.sleep(5)

                except Exception as ex:
                    logger.error(f"Error enriching article {article.id}: {ex}")
                    session.rollback()
            
        except KeyboardInterrupt:
            logger.info("AI Worker stopping...")
            break
        except Exception as e:
            logger.error(f"AI Worker loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_ai_worker()
