import os
import pickle
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token_calendar.pickle'):
        with open('token_calendar.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token_calendar.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def detect_scheduling_intent(email_text):
    """
    Naively detect if an email is asking to schedule a meeting.
    """
    keywords = ['schedule', 'meeting', 'call', 'calendar', 'appointment']
    return any(word in email_text.lower() for word in keywords)

def create_calendar_event(summary, body, start_time, duration_hours=1):
    """
    Create a real Google Calendar event.
    """
    service = get_calendar_service()
    end_time = start_time + datetime.timedelta(hours=duration_hours)

    event = {
        'summary': summary or 'Meeting',
        'description': body,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [],  # You can pass emails here if needed
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink')
