import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
SQLITE_FILE_NAME = os.getenv("SQLITE_FILE_NAME", "data/locusum_buffer.db")
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=False)

class RawArticle(SQLModel, table=True):
    __tablename__ = "raw_articles"

    id: str = Field(primary_key=True, description="SHA-256 hash of the URL")
    url: str = Field(unique=True, index=True)
    source: str
    title: Optional[str] = None
    html_content: str
    fetched_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    status: str = Field(default="NEW")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
