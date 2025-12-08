# ai.py
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ładuj .env z katalogu projektu
BASE_DIR = Path(__file__).parent.parent.resolve()
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Model trzymaj w .env, ale daj sensowny default
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

def call_gemini(prompt: str, system_instruction: str | None = None) -> str:
    if not API_KEY:
        return "Gemini API error: missing API key."

    url = f"{BASE_URL}{MODEL}:generateContent"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7},
    }

    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(f"{url}?key={API_KEY}",
                             headers=headers,
                             data=json.dumps(payload))
        if resp.status_code == 404:
            return f"Gemini API error (404): model {MODEL} not found."
        if resp.status_code == 429:
            return "Gemini API error (429): quota or rate limit exceeded."
        if not resp.ok:
            return f"Gemini API error ({resp.status_code}): {resp.text}"

        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        )
        return text or "Gemini returned an empty response."

    except Exception as e:
        return f"Gemini API error: {e}"
