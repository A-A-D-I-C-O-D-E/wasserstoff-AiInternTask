import os
import requests
from sqlalchemy.orm import sessionmaker
from database.db_connector import SessionLocal
from database.models import Email
from email_integration.email_parser import is_question_email
from tool_integrations.web_search import web_search

# Hugging Face API setup
HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


def enhance_email_summary_with_search(email_body: str) -> str:
    """
    If the email contains a question, enhance it with web search results.
    """
    if is_question_email(email_body):
        print("🔍 Question detected in email. Running web search...")
        search_results = web_search(email_body[:200])  # First 200 characters as query

        if search_results:
            snippets = "\n".join(
                [f"{result['title']}: {result['snippet']}" for result in search_results]
            )
            enhanced_prompt = (
                f"The following email contains a question:\n\n{email_body}\n\n"
                f"Here are some relevant results from the web:\n{snippets}\n\n"
                f"Please generate a helpful and factual summary."
            )
            return enhanced_prompt

    return email_body  # Return original if no question detected


def summarize_email_by_msg_id(message_id: str, parsed_email_data: dict = None) -> str:
    """
    Summarizes the email with the given message_id using Hugging Face API.
    If email is not found in the DB, it will try to insert from parsed_email_data.
    """
    if not HF_API_KEY:
        return "❌ Error: Hugging Face API key not found. Please set HF_API_KEY."

    session = SessionLocal()
    try:
        # Try to fetch existing email
        email_entry = session.query(Email).filter(Email.message_id == message_id).first()

        # Auto-save if not found and data is provided
        if not email_entry and parsed_email_data:
            print(f"📥 Inserting missing email with message_id {message_id}")
            email_entry = Email(
                message_id=message_id,
                sender=parsed_email_data.get("sender", "unknown"),
                subject=parsed_email_data.get("subject", ""),
                body=parsed_email_data.get("body", ""),
                received_at=parsed_email_data.get("received_at"),
                is_read=parsed_email_data.get("is_read", False),
                thread_id=parsed_email_data.get("thread_id")
            )
            session.add(email_entry)
            session.commit()

        # Still not found, return error
        if not email_entry:
            return "❌ Error: Email not found in the database and no parsed_email_data provided."

        email_body = email_entry.body.strip()
        if not email_body:
            return "❌ Error: Email body is empty."

        if len(email_body) > 10000:
            return "❌ Error: Email body is too long for summarization."

        # Enhance with web search if needed
        enhanced_text = enhance_email_summary_with_search(email_body)

        payload = {
            "inputs": enhanced_text,
            "parameters": {
                "max_length": 150,
                "min_length": 30,
                "do_sample": False,
                "truncation": True
            }
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            result = response.json()
            summary_text = result[0].get("summary_text", "[No summary returned]")
            email_entry.summary = summary_text
            session.commit()
            return f"✅ Summary saved for message_id {message_id}: {summary_text}"

        elif response.status_code == 400:
            return "❌ Bad request to Hugging Face API. Check input format."
        elif response.status_code == 403:
            return "❌ Invalid or expired Hugging Face API key."
        elif response.status_code == 429:
            return "⏳ Hugging Face API rate limit exceeded. Please try again later."
        else:
            return f"❌ Hugging Face API error {response.status_code}: {response.text}"

    except Exception as e:
        return f"❌ Unexpected error: {e}"

    finally:
        session.close()
