import google.generativeai as genai
import os

# Ensure your API key is loaded. If not using .env, paste it directly inside "" for this test.
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"Checking models for Key: {api_key[:5]}...")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error connecting to Google: {e}")