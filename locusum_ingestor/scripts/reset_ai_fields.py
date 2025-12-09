from locusum_ingestor.models.main_db import get_session, Article
from sqlmodel import select

def reset_ai_fields():
    session = get_session()
    statement = select(Article)
    articles = session.exec(statement).all()
    
    print(f"Resetting AI fields for {len(articles)} articles...")
    for article in articles:
        article.summary = None
        article.embedding = None
        session.add(article)
    
    session.commit()
    print("Reset complete.")

if __name__ == "__main__":
    reset_ai_fields()
