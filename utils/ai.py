import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).parent.parent.resolve()
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = "gemini-2.0-flash-exp"  # stabilny model REST
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"
URL = f"{BASE_URL}{MODEL}:generateContent"

print("[utils.ai] Gemini API KEY loaded:", "YES" if API_KEY else "NO")


def call_gemini(prompt: str, system_instruction: str = None) -> str:
    if not API_KEY:
        return "Gemini API error: missing API key."

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }

    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(
            f"{URL}?key={API_KEY}",
            headers=headers,
            data=json.dumps(payload)
        )

        if resp.status_code != 200:
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
