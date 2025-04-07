from bs4 import BeautifulSoup
import base64
from database.models import Email
from database.db_connector import SessionLocal
import re
import chardet
from email_integration.utils import contains_scheduling_intent, extract_datetime
from tool_integrations.calendar_integration import create_calendar_event
from lxml import etree


def handle_calendar_from_email(subject, body):
    if contains_scheduling_intent(body):
        dt = extract_datetime(body)
        if dt:
            link = create_calendar_event(subject, body, dt)
            return f"🗕️ Calendar event created: {link}"
    return None


def is_question_email(text):
    question_words = ["what", "when", "where", "how", "who", "why", "is", "are", "do", "does", "can", "should", "could"]
    lines = text.lower().splitlines()
    for line in lines:
        if line.strip().endswith("?") or any(line.strip().startswith(qw) for qw in question_words):
            return True
    return False


def build_reply_prompt(email_subject, email_body, thread_history=None):
    context = f"Subject: {email_subject}\n\n"
    if thread_history:
        context += f"Thread History:\n{thread_history}\n\n"
    context += f"Latest Email:\n{email_body}\n\n"
    context += "Write a polite, professional, and helpful reply to this email:"
    return context


import re

from lxml import etree

def sanitize_html(html):
    """
    Sanitizes HTML using lxml to ensure well-formed structure.
    Falls back to the original HTML if parsing fails.
    """
    try:
        parser = etree.HTMLParser(recover=True)
        tree = etree.fromstring(html, parser=parser)
        return etree.tostring(tree, method="html", encoding="unicode")
    except Exception as e:
        print(f"Error sanitizing HTML: {e}")
        return html  # Fallback to original HTML

def decode_and_clean(data):
    if isinstance(data, str):
        data = data.encode('utf-8')

    detected_encoding = chardet.detect(data)['encoding']
    try:
        decoded = base64.urlsafe_b64decode(data).decode(detected_encoding, errors='replace')
    except Exception as e:
        print(f"Error decoding with detected encoding {detected_encoding}: {e}")
        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

    cleaned = sanitize_html(decoded)
    return sanitize_special_chars(cleaned)


def sanitize_special_chars(text):
    """
    Removes or replaces non-UTF-8 compatible characters (surrogates, control chars, etc.).
    Keeps mostly printable ASCII and common Unicode.
    """
    # Remove surrogate characters that can't be encoded in UTF-8
    text = re.sub(r'[\ud800-\udfff]', '', text)

    # Optionally remove other non-printable/control characters (except line breaks)
    text = re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', text)

    return text


def parse_email(message):
    headers = message['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '[No Subject]')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), '[No Sender]')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), '[No Date]')
    message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)
    in_reply_to = next((h['value'] for h in headers if h['name'] == 'In-Reply-To'), None)
    thread_id = message.get('threadId')

    body = None
    payload = message['payload']

    # Fallback if parts is not present
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType')
            data = part['body'].get('data')
            if data and (mime_type == 'text/plain' or mime_type == 'text/html'):
                body = decode_and_clean(data)
                break
    else:
        data = payload['body'].get('data')
        if data:
            body = decode_and_clean(data)

    parsed_data = {
        'subject': subject,
        'sender': sender,
        'date': date,
        'body': body if body else '[No body found]',
        'message_id': message_id,
        'in_reply_to': in_reply_to,
        'thread_id': thread_id,
    }

    return parsed_data



def process_email_message(service, message, summary, thread_id, message_id, in_reply_to):
    session = SessionLocal()

    parsed = parse_email(message)
    sender = parsed['sender']
    subject = parsed['subject']
    date = parsed['date']
    body = parsed['body']

    email = Email(
        sender=sender,
        subject=subject,
        body=body,
        date=date,
        summary=summary,
        thread_id=thread_id,
        message_id=message_id,
        in_reply_to=in_reply_to
    )

    session.add(email)
    session.commit()

    return f"✅ Email from {sender} processed and stored."
