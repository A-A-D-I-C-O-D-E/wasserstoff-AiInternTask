from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

def create_message(to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    return service.users().messages().send(userId=user_id, body=message).execute()
