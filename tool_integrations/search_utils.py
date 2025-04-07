from email_integration.email_parser import is_question_email
from tool_integrations.web_search import web_search

def search_web_if_needed(text: str) -> str:
    """
    Check if the input text seems to ask a question. If so, perform a web search
    and return formatted results. Otherwise, return an empty string.
    """
    if is_question_email(text):
        print("🔍 Detected a question — performing web search...")
        return web_search(text[:200])  # Use first 200 characters
    else:
        print("ℹ️ No question detected. Skipping web search.")
        return ""
