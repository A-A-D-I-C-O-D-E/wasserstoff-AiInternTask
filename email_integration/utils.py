import dateparser

def contains_scheduling_intent(body: str) -> bool:
    keywords = ["meeting", "schedule", "call", "appointment", "catch up", "sync"]
    for keyword in keywords:
        if keyword in body.lower():
            return True
    return False

def extract_datetime(text: str):
    return dateparser.parse(text)

def is_question_email(text: str) -> bool:
    question_words = ["what", "when", "where", "how", "who", "why", "is", "are", "do", "does", "can", "should", "could"]
    lines = text.lower().splitlines()
    for line in lines:
        if line.strip().endswith("?") or any(line.strip().startswith(qw) for qw in question_words):
            return True
    return False
