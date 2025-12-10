import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Force load env vars immediately
load_dotenv(find_dotenv(), override=True)

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

MODEL = "gemini-2.5-flash-preview-09-2025" 
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"
URL = f"{BASE_URL}{MODEL}:generateContent"

print(f"[utils.ai] Gemini API KEY loaded: {'YES' if API_KEY else 'NO'}")

def call_gemini(prompt: str, system_instruction: str = None, media_data: dict = None) -> str:
    """
    Unified entry point to call Gemini with Text, Images, or Documents (PDF).
    """
    if not API_KEY:
        return "Gemini API error: missing API key."

    # 1. Build Payload
    user_parts = [{"text": prompt}]
    
    if media_data:
        user_parts.append({
            "inline_data": {
                "mime_type": media_data["mime_type"],
                "data": media_data["data"]
            }
        })

    payload = {
        "contents": [{"parts": user_parts}],
        "generationConfig": {"temperature": 0.7}
    }

    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    headers = {"Content-Type": "application/json"}

    # 2. Retry Logic
    max_retries = 5
    base_wait = 2 

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                f"{URL}?key={API_KEY}",
                headers=headers,
                data=json.dumps(payload)
            )

            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates: return "Gemini returned no candidates."
                
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts: return "Gemini returned no text content."
                
                return parts[0].get("text", "")

            # Retry if 429 (Rate Limit) OR 503 (Server Overloaded)
            elif resp.status_code in [429, 503]:
                wait_time = base_wait * (2 ** attempt)
                print(f"[utils.ai] Server busy/limit ({resp.status_code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            else:
                return f"Gemini API error ({resp.status_code}): {resp.text}"

        except Exception as e:
            return f"Gemini API connection error: {e}"

    return "Gemini API error: Service unavailable after retries."