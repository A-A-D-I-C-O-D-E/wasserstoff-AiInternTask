
# 🧠 wasserstoff-AiInternTask

A smart AI-powered **Personal Email Assistant** built as part of the **Wasserstoff AI Internship Task**.  
It fetches unread emails, summarizes them using LLMs, detects calendar intent, sends Slack notifications, and drafts replies — showcasing AI integration and automation skills.

---

## 🚀 Features

- ✅ Fetch unread emails via Gmail API  
- 🧠 Summarize email content using Hugging Face’s BART model  
- 🗓️ Detect scheduling intent and create Google Calendar events  
- 🔁 Thread-aware context gathering for smart replies  
- 📨 Auto-generate reply drafts with option to confirm  
- 🔔 Send Slack notifications for each processed email  
- 💾 Store and update email data in SQLite using SQLAlchemy  
- 🧰 Modular and extensible project structure  

---

## 🗂️ Project Structure

```
AiInternTask/
├── app.py
├── check.py
├── credentials.json
├── emails.db
├── requirements.txt
├── .env
│
├── database/
│   ├── __init__.py
│   ├── db_connector.py
│   └── models.py
│
├── email_integration/
│   ├── __init__.py
│   ├── credentials.json
│   ├── email_fetcher.py
│   ├── email_parser.py
│   ├── email_sender.py
│   ├── threading_utils.py
│   ├── token.json
│   └── utils.py
│
├── email_integration/utils/
│   ├── __init__.py
│   ├── reply_utils.py
│   └── summarizer.py
│
└── tool_integrations/
    ├── __init__.py
    ├── calendar_integration.py
    ├── credential.json
    ├── search_utils.py
    ├── slack_integration.py
    └── web_search.py
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/aditya-gupta/wasserstoff/AiInternTask.git
cd AiInternTask
```

### 2. Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Setup Gmail API Credentials

- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Enable **Gmail** & **Calendar** APIs
- Create OAuth client ID and download the `credentials.json`
- Place it in the `credentials/` directory

### 4. Setup Slack Webhook

- Go to [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- Create a new webhook and copy the URL
- Add it to your `.env` file as `SLACK_WEBHOOK_URL=your_webhook_url`

### 5. Run the App

```bash
python app.py
```

---

## 🧠 Architecture Overview

### ⟲ Flow:

1. Emails are fetched via Gmail API  
2. Each email is parsed and stored in SQLite  
3. Email body is passed to the BART LLM for summarization  
4. Context-aware reply is generated  
5. If scheduling intent is detected, a calendar event is created  
6. A Slack notification is sent for every processed email  

### 🗂️ Components

- **Gmail API** – Email fetching  
- **Hugging Face BART** – Summarization & reply generation  
- **Google Calendar API** – Schedule meeting slots  
- **Slack API** – Notify updates  
- **SQLite** – Store email history and summaries  

---

## 📽️ Video Walkthrough

A short demo video is included  demonstrating:

- Running the app  
- Fetching and summarizing emails  
- Detecting scheduling intent  
- Sending Slack notifications and replies  

---

Windows
pip install -r requirements.txt
```

### 3. Setup Gmail API Credentials

- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Enable **Gmail** & **Calendar** APIs
- Create OAuth client ID and download the `credentials.json`
- Place it in the `email_integration/` directory

### 4. Setup Slack Webhook

- Go to [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- Create a new webhook and copy the URL
- Add it to your `.env` file or directly in `slack_integration.py` (for testing only)

### 5. Run the App

```bash
python app.py
```

---

## 🧠 Architecture Overview

### ⟲ Flow:

1. Emails are fetched via Gmail API  
2. Each email is parsed and stored in SQLite  
3. Email body is passed to the BART LLM for summarization  
4. Context-aware reply is generated  
5. If scheduling intent is detected, a calendar event is created  
6. A Slack notification is sent for every processed email  

### 🗍️ Components

- **Gmail API** – Email fetching  
- **Hugging Face BART** – Summarization & reply generation  
- **Google Calendar API** – Schedule meeting slots  
- **Slack API** – Notify updates  
- **SQLite** – Store email history and summaries  

---

## 📟️ Video Walkthrough

A short demo video is included (or to be provided via link) demonstrating:

- Running the app  
- Fetching and summarizing emails  
- Detecting scheduling intent  
- Sending Slack notifications and replies  

---


This project was created as part of an internship assessment task and is free for non-commercial educational use.

---

