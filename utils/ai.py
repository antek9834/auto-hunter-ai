import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).parent.parent.resolve()
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# UPDATE: Use the same stable model as CarSearchService
MODEL = "gemini-2.5-flash-preview-09-2025" 
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"
URL = f"{BASE_URL}{MODEL}:generateContent"

print(f"[utils.ai] Gemini API KEY loaded: {'YES' if API_KEY else 'NO'}")

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

    # --- RETRY LOGIC FOR 429 ERRORS ---
    max_retries = 3
    base_wait = 2 # seconds

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                f"{URL}?key={API_KEY}",
                headers=headers,
                data=json.dumps(payload)
            )

            # Success
            if resp.status_code == 200:
                data = resp.json()
                text = (
                    data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                )
                return text or "Gemini returned an empty response."

            # Rate Limit Error
            elif resp.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = base_wait * (2 ** attempt) # Exponential backoff: 2, 4, 8...
                    print(f"[utils.ai] Rate limit hit (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"Gemini API error (429): Rate limit exceeded after {max_retries} retries."

            # Other Errors
            else:
                return f"Gemini API error ({resp.status_code}): {resp.text}"

        except Exception as e:
            return f"Gemini API connection error: {e}"

    return "Gemini API error: Unknown failure."