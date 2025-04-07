import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def google_search(query, num_results=3):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = [
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            }
            for item in data.get("items", [])
        ]
        return results

    except requests.exceptions.RequestException as e:
        print("Search API error:", e)
        return []

def web_search(query: str) -> str:
    results = google_search(query)
    if not results:
        return "No relevant results found."

    response_text = "\n\n".join(
        f"🔎 {item['title']}\n{item['snippet']}\n🔗 {item['link']}"
        for item in results
    )
    return response_text
