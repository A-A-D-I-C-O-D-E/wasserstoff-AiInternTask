# # # # from email_integration.email_parser import extract_email_details

# # # # Example usage
# # # from email_integration.email_fetcher import authenticate_gmail, fetch_emails
# # # from email_integration.email_parser import parse_email


# # # if __name__ == "__main__":
# # #     print("🚀 Running email parsing test...")

# # #     # Step 1: Authenticate
# # #     service = authenticate_gmail()

# # #     # Step 2: Fetch emails
# # #     emails = fetch_emails(service, query="")

# # #     # Step 3: Parse and show sample email data
# # #     for i, raw in enumerate(emails[:5], 1):  # Limit to first 5
# # #         parsed = parse_email(raw)
# # #         print(f"\n📧 Email {i}")
# # #         print("Subject:", parsed["subject"])
# # #         print("From:", parsed["sender"])
# # #         print("Date:", parsed["date"])
# # #         print("Body (preview):", parsed["body"][:150])
# # from tool_integrations.web_search import google_search

# # results = google_search("what is generative AI?")
# # for result in results:
# #     print(f"{result['title']}\n{result['link']}\n{result['snippet']}\n")
# from sqlalchemy import inspect, create_engine

# # Make sure to only use the correct database path once
# engine = create_engine("sqlite:///app.db")  # Replace with your actual DB if needed
# inspector = inspect(engine)

# try:
#     columns = inspector.get_columns("emails")
#     print([col['name'] for col in columns])
# except Exception as e:
#     print("Error:", e)
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base
# from database.models import Email

# Base = declarative_base()

# engine = create_engine("sqlite:///app.db")

# # This will create the table if it doesn't already exist
# Email.__table__.create(bind=engine, checkfirst=True)

# print("Table created or already exists.")
# from sqlalchemy.orm import sessionmaker

# from sqlalchemy import create_engine

# engine = create_engine("sqlite:///app.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# emails = session.query(Email).all()
# for email in emails:
#     print(email.subject)
from sqlalchemy import inspect, create_engine

engine = create_engine("sqlite:///app.db")
inspector = inspect(engine)
columns = inspector.get_columns("emails")
print("Existing columns:", [col["name"] for col in columns])