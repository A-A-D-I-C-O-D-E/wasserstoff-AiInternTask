import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Slack token from environment variable
SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL_ID")  # Use Channel ID instead of name

# Initialize Slack client
client = WebClient(token=SLACK_TOKEN)

def send_to_slack(message):
    """Send a message to a Slack channel."""
    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,  # Use Channel ID
            text=message
        )
        return response
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        return None
