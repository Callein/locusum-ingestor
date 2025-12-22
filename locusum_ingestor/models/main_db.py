
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, create_engine, Session
from sqlalchemy import Column, BigInteger
from pgvector.sqlalchemy import Vector
import os

from dotenv import load_dotenv

load_dotenv()

# Database Connection
# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Default to Docker service name 'db' if not specified
    user = os.getenv("POSTGRES_USER", "locusum")
    password = os.getenv("POSTGRES_PASSWORD", "locusum_password")
    host = os.getenv("POSTGRES_HOST", "db")
    db_name = os.getenv("POSTGRES_DB", "locusum")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{db_name}"

engine = create_engine(DATABASE_URL, echo=False)

class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True))
    raw_id: str = Field(index=True, description="Reference to SQLite raw_articles.id")
    url: str = Field(unique=True, index=True)
    source: str
    region: Optional[str] = Field(default=None, index=True)
    author: Optional[str] = None
    image_url: Optional[str] = None
    title: Optional[str] = None
    content: str
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    
    # pgvector embedding column (1536 dims for OpenAI)
    embedding: Optional[list[float]] = Field(default=None, sa_column=Column(Vector(768)))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

from sqlalchemy import text

def create_db_and_tables():
    # Check for RESET_DB env var to drop tables
    if os.getenv("RESET_DB", "false").lower() == "true":
        # Only print log, avoid using print if logger is available, but for now print is fine
        print("RESET_DB is set to true. Dropping all tables in Main DB...")
        SQLModel.metadata.drop_all(engine)
        
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
