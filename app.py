import os
from email_integration.email_fetcher import authenticate_gmail, fetch_emails
from email_integration.email_parser import parse_email
from llm_integration.summarizer import summarize_email_by_msg_id
from database.db_connector import save_email_to_db, SessionLocal
from database.models import Email
from tool_integrations.slack_integration import send_to_slack
from llm_integration.reply_utils import build_reply_prompt, generate_reply
from email_integration.email_sender import create_message, send_message
from email_integration.threading_utils import get_thread_context
from tool_integrations.calendar_integration import detect_scheduling_intent, create_calendar_event
from tool_integrations.search_utils import search_web_if_needed


def handle_auto_reply(service, email_data):
    print(f"\n📬 Handling auto-reply for: {email_data['subject']}")
    
    prompt = build_reply_prompt(
        email_data['subject'],
        email_data['body'],
        email_data.get('thread_context', '')
    )
    prompt = search_web_if_needed(prompt)
    
    reply = generate_reply(prompt)
    print("🧠 Generated Reply:\n", reply)
    
    confirm = input("✅ Send this reply? (y/n): ").strip().lower()
    if confirm == 'y':
        message = create_message(email_data['sender'], f"Re: {email_data['subject']}", reply)
        send_message(service, "me", message)
        print("📤 Reply sent!")
    else:
        print("❌ Reply skipped.")


def main():
    print("🚀 Starting AI Email Assistant")
    service = authenticate_gmail()
    db_session = SessionLocal()

    raw_emails = fetch_emails(service, db_session, query="is:unread") or []
    print(f"✅ Total emails fetched: {len(raw_emails)}")

    processed, skipped = 0, 0

    for i, msg in enumerate(raw_emails[:50], 1): # Limit to 50 emails for demo purposes
        print(f"\n--- 📧 Processing Email {i} ---")
        try:
            parsed = parse_email(msg)

            if not parsed["body"].strip():
                print("⚠️ Skipping email due to empty body.")
                skipped += 1
                continue

            parsed["body"] = parsed["body"][:4000]  # Trim long bodies

            # 🧠 Summarize email using message_id
            print("🧠 Summarizing email...")
            summary = summarize_email_by_msg_id(parsed["message_id"])

            # 🧵 Get thread context
            print("🧵 Getting thread context...")
            thread_context = get_thread_context(parsed["thread_id"], db_session)

            # 💾 Save to DB if not already saved
            existing = db_session.query(Email).filter_by(message_id=parsed["message_id"]).first()
            if not existing:
                print("💾 Saving to database...")
                save_email_to_db(
                    sender=parsed["sender"],
                    subject=parsed["subject"],
                    body=parsed["body"],
                    summary=summary,
                    message_id=parsed["message_id"],
                    thread_id=parsed["thread_id"],
                    in_reply_to=parsed["in_reply_to"]
                )
            else:
                print("📌 Email already in DB (summary still updated in memory).")

            # 📅 Check for calendar intent
            if detect_scheduling_intent(parsed["body"]):
                print("📅 Scheduling intent detected, creating calendar event...")
                create_calendar_event(parsed["body"], parsed["sender"])
            else:
                print("📅 No scheduling intent detected.")

            # 📨 Send Slack notification
            print("📨 Sending Slack notification...")
            slack_msg = (
                f"*New Email*\n"
                f"From: {parsed['sender']}\n"
                f"Subject: {parsed['subject']}\n"
                f"Summary: {summary[:1000]}"
            )
            send_to_slack(slack_msg)

            # ✉️ Handle auto-reply
            reply_data = {
                'sender': parsed["sender"],
                'subject': parsed["subject"],
                'body': parsed["body"],
                'thread_context': thread_context
            }
            handle_auto_reply(service, reply_data)

            processed += 1

        except Exception as e:
            print(f"❌ Error processing email {i}: {e}")
            skipped += 1

    db_session.close()

    print(f"\n✅ Done! Processed: {processed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
