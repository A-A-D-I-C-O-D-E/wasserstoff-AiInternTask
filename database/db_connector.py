import os
import json
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Text,DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


# Load environment variables from a .env file if needed
load_dotenv()

# Define the path to your SQLite database
DATABASE_URL = "sqlite:///./emails.db"  # Creates emails.db in the current directory

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM base
Base = declarative_base()

# Email table model
class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False, default="me@example.com")
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    thread_id = Column(String(255), nullable=True)
    message_id = Column(String(255), nullable=True)
    in_reply_to = Column(String(255), nullable=True)
    date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    

# Create tables
Base.metadata.create_all(bind=engine)

import json

import uuid

def save_email_to_db(sender, subject, body, summary, thread_id=None, message_id=None, in_reply_to=None, recipient="me@example.com",):
    db = SessionLocal()
    try:
        # Fallback to auto-generated values if None
        if not message_id:
            message_id = f"<{uuid.uuid4()}@autogen.local>"
        if not thread_id:
            thread_id = str(uuid.uuid4())  # simple UUID thread ID

        email_entry = Email(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            summary=summary,
            thread_id=thread_id,
            message_id=message_id,
            in_reply_to=in_reply_to,
            
        )
        db.add(email_entry)
        db.commit()
        db.refresh(email_entry)
        print("✅ Email saved successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving email: {e}")
    finally:
        db.close()




# Provide session to other modules
def get_db_session():
    return SessionLocal()
