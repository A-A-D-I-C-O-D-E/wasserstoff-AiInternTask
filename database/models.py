import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, Text,
    ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Load environment variables from a .env file
load_dotenv()

# Fetch database credentials
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root123")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "email")

# Encode password for special characters
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Database URL (MySQL)
DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# Define base
Base = declarative_base()

# Create engine and session
try:
    engine = create_engine(DATABASE_URL, echo=os.getenv("DEBUG", "false").lower() == "true")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with engine.connect() as conn:
        print("✅ Successfully connected to the database.")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Email model
class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender = Column(String(255), nullable=False, index=True)
    recipient = Column(String(255), nullable=False, default="me@example.com")
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    thread_id = Column(String(255), index=True)
    message_id = Column(String(255), unique=True, nullable=False)
    in_reply_to = Column(String(255), nullable=True)
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_thread_sender", "thread_id", "sender"),
        {'extend_existing': True}
    )

# Attachment model
class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'))

    filename = Column(String(255))
    mime_type = Column(String(100))
    size = Column(Integer)
    download_url = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email")


# Create tables
Base.metadata.create_all(bind=engine)
print("✅ Tables created or already exist.")
