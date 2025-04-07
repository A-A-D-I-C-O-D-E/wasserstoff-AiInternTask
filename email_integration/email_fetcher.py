import os
import sys
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup
from base64 import urlsafe_b64decode

from database.db_connector import SessionLocal
from database.models import Email

# Load environment variables from .env file
load_dotenv()

# Ensure stdout supports UTF-8
sys.stdout.reconfigure(encoding='utf-8')


def clean_text(text):
    if not text:
        return ""
    return text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")


def get_header_value(headers, name):
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return None


def extract_email_body(payload):
    parts = payload.get('parts', [])
    body = payload.get('body', {}).get('data')

    if parts:
        for part in parts:
            if part.get('mimeType') == 'text/html':
                data = part['body'].get('data')
                if data:
                    decoded = urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8', 'ignore')
                    return clean_text(BeautifulSoup(decoded, "html.parser").get_text())

    if body:
        decoded = urlsafe_b64decode(body.encode('UTF-8')).decode('UTF-8', 'ignore')
        return clean_text(BeautifulSoup(decoded, "html.parser").get_text())

    return ""


def process_message(message, session):
    headers = message['payload']['headers']
    payload = message['payload']

    sender = clean_text(get_header_value(headers, 'From'))
    subject = clean_text(get_header_value(headers, 'Subject') or "No Subject")
    date = get_header_value(headers, 'Date')
    thread_id = message.get('threadId')
    message_id = get_header_value(headers, 'Message-ID')
    in_reply_to = get_header_value(headers, 'In-Reply-To')
    body = clean_text(extract_email_body(payload))

    email_obj = Email(
        sender=sender,
        recipient="me@example.com",
        subject=subject,
        body=body,
        summary=None,
        thread_id=thread_id,
        message_id=message_id,
        in_reply_to=in_reply_to
    )
    session.add(email_obj)


def authenticate_gmail():
    print("🔄 Authenticating with Gmail...")

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")

    if not os.path.exists(CREDENTIALS_PATH):
        print("❌ ERROR: 'credentials.json' not found!")
        exit(1)

    if os.path.exists(TOKEN_PATH):
        print("✅ Found token.json. Loading credentials...")
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("🌐 No valid credentials. Starting new OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        print("✅ Credentials saved to token.json.")

    return build('gmail', 'v1', credentials=creds)


def fetch_emails(service, session, query=""):
    emails = []
    try:
        print("📩 Fetching emails from Gmail...")
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        print(f"🔍 Found {len(messages)} messages.")

        for idx, message in enumerate(messages, 1):
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                process_message(msg, session)
                emails.append(msg)
                snippet = clean_text(msg.get('snippet', ''))[:60]
                print(f"✅ Processed email {idx}/{len(messages)}: {snippet}")
            except Exception as e:
                print(f"❌ Error processing email {idx}: {clean_text(str(e))}")

        session.commit()
        print(f"✅ All {len(emails)} emails saved to database.")

    except HttpError as error:
        print(f"❌ Gmail API error: {clean_text(str(error))}")
        session.rollback()

    return emails


if __name__ == "__main__":
    print("🚀 Starting Email Fetching Script...")
    service = authenticate_gmail()

    db_session = SessionLocal()
    fetch_emails(service, db_session, query="")  # Optional: "is:unread"
    db_session.close()
