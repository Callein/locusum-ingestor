import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# Priority: DATABASE_URL env var > POSTGRES_* env vars > SQLite default (fallback)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Try to construct from POSTGRES_* vars
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    db_name = os.getenv("POSTGRES_DB")
    
    if user and host and db_name:
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{db_name}"
    else:
        # Fallback to SQLite if no Postgres config found
        SQLITE_FILE_NAME = os.getenv("SQLITE_FILE_NAME", "data/locusum_buffer.db")
        DATABASE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(DATABASE_URL, echo=False)

class RawArticle(SQLModel, table=True):
    __tablename__ = "raw_articles"

    id: str = Field(primary_key=True, description="SHA-256 hash of the URL")
    url: str = Field(unique=True, index=True)
    source: str
    region: Optional[str] = Field(default=None)
    author: Optional[str] = None
    image_url: Optional[str] = None
    title: Optional[str] = None
    html_content: str
    fetched_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    status: str = Field(default="NEW")

def create_db_and_tables():
    # Check for RESET_DB env var to drop tables
    if os.getenv("RESET_DB", "false").lower() == "true":
        print("RESET_DB is set to true. Dropping all tables...")
        SQLModel.metadata.drop_all(engine)
    
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
