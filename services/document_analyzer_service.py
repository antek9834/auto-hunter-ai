import json
import os
from services.document_processor import DocumentProcessor
from utils.ai import call_gemini

# Safe import for tracing

try:
    from langfuse.decorators import observe, langfuse_context
    print("[System] Langfuse library found. Tracing enabled.")
except ImportError:
    print("[System] Langfuse library NOT found. Tracing disabled.")
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

class DocumentAnalyzerService:
    def __init__(self):
        self.processor = DocumentProcessor()
        # Locate the prompt file relative to this script
        self.prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/document_analysis_prompt.txt")

    @observe(name="document_analysis")
    def analyze(self, uploaded_file, price, mileage):
        # 1. Process File using your new Service
        # This should return {'mime_type': '...', 'data': '...'} based on our previous step
        media_payload = self.processor.process(uploaded_file)
        
        if "error" in media_payload:
            return {"error": media_payload["error"]}

        # 2. Load and Format Prompt
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                raw_prompt = f.read()
            
            # Simple string replacement for dynamic values
            final_prompt = raw_prompt.replace("{{price}}", str(price)).replace("{{mileage}}", str(mileage))
        except FileNotFoundError:
            return {"error": "Prompt file not found."}

        # 3. Call AI (Unified)
        # We pass the media_payload directly. Gemini 2.5 Flash handles PDF/Images natively.
        response_text = call_gemini(
            prompt=final_prompt, 
            media_data=media_payload 
        )

        # 4. Clean & Parse JSON
        try:
            # Strip markdown code blocks if present (e.g. ```json ... ```)
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            start = clean_text.find("{")
            end = clean_text.rfind("}") + 1
            if start == -1 or end == 0:
                 raise ValueError("No JSON found")
                 
            return json.loads(clean_text[start:end])
        except Exception:
            return {
                "vehicle_identity": "Unknown",
                "summary": "AI response was not valid JSON.",
                "raw_response": response_text,
                "red_flags": ["Parse Error - See Raw Response"],
                "price_verdict": "Unknown",
                "recommendation": "Check raw output."
            }