import json
import os
import backoff
import requests
from pathlib import Path
from typing import Dict, Any, List

# --- SAFE IMPORT FOR LANGFUSE ---
try:
    from langfuse.decorators import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
# --------------------------------

from tools.standvirtual_scraper import StandvirtualScraper

class CarSearchService:
    
    LLM_MODEL = "gemini-2.5-flash-preview-09-2025"
    API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

    def __init__(self):
        print("[Service] Initializing Standvirtual Scraper...")
        self.scraper = StandvirtualScraper()
        
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        self.api_url = f"{self.API_BASE_URL}{self.LLM_MODEL}:generateContent"
        
        if not self.api_key:
            print("[Service Init] WARNING: LLM API key not found. AI features are disabled.")
        else:
            print(f"[Service Init] LLM API key loaded.")
        
        # --- LOAD PROMPT FROM FILE (WITH FALLBACK) ---
        self.parse_system_prompt = self._load_prompt("car_query.txt")
        
        # Fallback if file load failed
        if not self.parse_system_prompt:
            print("[Service Init] Prompt file empty or missing. Using hardcoded fallback.")
            self.parse_system_prompt = (
                "You are a helpful assistant that extracts structured search parameters from a user's car search query. "
                "The search will be conducted on Standvirtual. Output MUST be valid JSON. "
                "Extract fields: brand, model, min_price, max_price, min_year, max_km, fuel, location. "
                "Rules: If missing, use null. Convert 'k' to thousands."
            )

        self.parse_schema = {
            "type": "OBJECT",
            "properties": {
                "brand": {"type": "STRING", "nullable": True},
                "model": {"type": "STRING", "nullable": True},
                "min_price": {"type": "INTEGER", "nullable": True},
                "max_price": {"type": "INTEGER", "nullable": True},
                "min_year": {"type": "INTEGER", "nullable": True},
                "max_km": {"type": "INTEGER", "nullable": True},
                "fuel": {"type": "STRING", "nullable": True},
                "location": {"type": "STRING", "nullable": True}
            }
        }

    def _load_prompt(self, filename: str) -> str:
        """
        Robustly resolves the path to the prompts folder and loads the file.
        """
        try:
            # 1. Resolve path relative to this file (services/car_search_system.py)
            current_dir = Path(__file__).parent.resolve()
            # Go up one level to project root, then into prompts
            project_root = current_dir.parent
            file_path = project_root / "prompts" / filename
            
            print(f"[Service Init] Loading prompt from: {file_path}")

            if not file_path.exists():
                print(f"[Service Init] ❌ File not found at: {file_path}")
                return ""

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    print(f"[Service Init] ✅ Prompt loaded ({len(content)} chars).")
                    return content
                else:
                    print(f"[Service Init] ⚠️ File found but empty: {filename}")
                    return ""
                    
        except Exception as e:
            print(f"[Service Init] Error loading prompt: {e}")
            return ""

    def _call_gemini_structured(self, user_prompt, system_instruction, response_schema):
        if not self.api_key:
            raise EnvironmentError("API key is not set.")
        
        @backoff.on_exception(
            backoff.expo, 
            (requests.exceptions.RequestException, json.JSONDecodeError), 
            max_tries=5
        )
        def attempt_call():
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [{"text": system_instruction}]},
                "generationConfig": { 
                    "responseMimeType": "application/json",
                    "responseSchema": response_schema,
                    "temperature": 0.0
                },
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.api_url}?key={self.api_key}", headers=headers, data=json.dumps(payload))
            
            if response.status_code != 200:
                print(f"[Gemini Error] Status: {response.status_code}. Response: {response.text[:200]}...")
                response.raise_for_status() 
            
            result = response.json()
            json_str = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
            return json.loads(json_str)

        return attempt_call()

    @observe(as_type="generation")
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        if not self.api_key: return {}
        try:
            filters = self._call_gemini_structured(user_query, self.parse_system_prompt, self.parse_schema)
            print(f"[parse_query] Parsed filters: {filters}")
            return filters
        except Exception as e:
            print(f"[parse_query] Error parsing query: {e}")
            return {}

    @observe(as_type="span")
    def search_cars(self, filters: dict) -> list:
        cleaned = {k: v for k, v in filters.items() if v is not None}
        try:
            print(f"[Scraper] Search initiated for: {cleaned}")
            return self.scraper.search(
                brand=cleaned.get('brand', ''), 
                model=cleaned.get('model', ''), 
                min_price=cleaned.get('min_price'),
                max_price=cleaned.get('max_price'), 
                min_year=cleaned.get('min_year')
            )
        except Exception as e:
            print(f"[search_cars] Error during scraping: {e}")
            return []

    @observe(as_type="generation")
    def rank_and_annotate(self, user_query: str, results: list) -> list:
        if not self.api_key or not results: return results 
        cars_to_process = results[:15]
        
        system_instr = (
            "You are a personalized car shopping assistant. "
            "Re-order list so best matches appear first. "
            "Write a short 'ai_description' (1 sentence) recommendation for each car."
        )

        simplified_input = [
            {"id": i, "title": c['title'], "price": c['price'], "year": c['year'], "km": c['km']} 
            for i, c in enumerate(cars_to_process)
        ]

        prompt = f"User Query: '{user_query}'\n\nListings to Rank:\n{json.dumps(simplified_input)}"

        response_schema = {
            "type": "OBJECT",
            "properties": {
                "ranked_cars": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "original_id": {"type": "INTEGER"},
                            "ai_description": {"type": "STRING"}
                        }
                    }
                }
            }
        }

        try:
            processed_data = self._call_gemini_structured(prompt, system_instr, response_schema)
            new_ordered_list = []
            for item in processed_data.get("ranked_cars", []):
                original_index = item.get("original_id")
                if original_index is not None and 0 <= original_index < len(cars_to_process):
                    car = cars_to_process[original_index]
                    car['ai_description'] = item.get("ai_description", "Matches your search criteria.")
                    new_ordered_list.append(car)
            
            if len(new_ordered_list) < len(cars_to_process):
                used_ids = {item.get("original_id") for item in processed_data.get("ranked_cars", [])}
                for i, car in enumerate(cars_to_process):
                    if i not in used_ids:
                        car['ai_description'] = "Also found matching your criteria."
                        new_ordered_list.append(car)
            return new_ordered_list
        except Exception as e:
            print(f"[rank_and_annotate] Error: {e}")
            return results 

    @observe(as_type="generation")
    def summarize_results(self, results: list, context_text: str = "") -> str:
        if not self.api_key or not results: return "Unable to generate summary."

        system_instr = (
            "You are a savvy car market expert. Review the listings and generate a concise summary. "
            "Highlight price range, best value option, and red flags. "
            "Reference user document context if provided."
        )
        
        context_block = f"\n\nUSER CONTEXT (Insurance/Prefs):\n{context_text}\n" if context_text else ""
        results_sample = json.dumps(results[:15], indent=2)
        full_prompt = f"{context_block}\n\nMARKET DATA:\n{results_sample}\n\nPlease provide a market snapshot:"

        try:
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "systemInstruction": {"parts": [{"text": system_instr}]},
                "generationConfig": {"temperature": 0.7}
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.api_url}?key={self.api_key}", headers=headers, data=json.dumps(payload))
            if response.status_code != 200: return "Error generating summary."
            return response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Analysis unavailable.')
        except Exception as e:
            return f"Error summarizing: {e}"

    @observe(as_type="generation")
    def chat_about_results(self, question: str, results: list, context_text: str = "") -> str:
        if not self.api_key: return "API key missing."
        
        chat_system_prompt = "You are a car analyst. Answer based ONLY on the provided listings."
        context_block = f"\n\nDOCUMENT CONTEXT:\n{context_text}\n" if context_text else ""
        results_json = json.dumps(results[:15], indent=2)
        full_prompt = f"{context_block}\n\nCAR LISTINGS (JSON):\n{results_json}\n\nUSER QUESTION: {question}"
        
        try:
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "systemInstruction": {"parts": [{"text": chat_system_prompt}]},
                "generationConfig": {"temperature": 0.5}
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.api_url}?key={self.api_key}", headers=headers, data=json.dumps(payload))
            return response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Error generating response.')
        except Exception as e:
            return f"Error: {e}"
            
    def __del__(self):
        try:
            if hasattr(self, 'scraper'): del self.scraper
        except: pass