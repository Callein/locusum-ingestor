
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, create_engine, Session
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
import os

from dotenv import load_dotenv

load_dotenv()

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in .env")

engine = create_engine(DATABASE_URL, echo=False)

class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: Optional[int] = Field(default=None, primary_key=True)
    raw_id: str = Field(index=True, description="Reference to SQLite raw_articles.id")
    url: str = Field(unique=True, index=True)
    source: str
    title: Optional[str] = None
    content: str
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    
    # pgvector embedding column (1536 dims for OpenAI)
    embedding: Optional[list[float]] = Field(default=None, sa_column=Column(Vector(1536)))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

from sqlalchemy import text

def create_db_and_tables():
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
