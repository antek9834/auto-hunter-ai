import os
import json

from utils.ai import call_gemini

#Import for Langfuse 
try:
    from langfuse.decorators import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func): return func
        return decorator

class OfferAnalysisService:
    """
    Service Layer responsible for evaluating car offers using Gemini.
    Implements structured data extraction and separation of concerns.
    """

    def __init__(self):
        # Loading prompt template from external text file - to separate logic from content/according to Week 2 classes
        prompt_path = os.path.join("prompts", "offer_analysis_prompt.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            # Fallback for safety reasones
            print(f"Warning: Prompt file not found at {prompt_path}")
            self.prompt_template = ""

    @observe(as_type="generation")
    def analyze(self, description, price, mileage, year, recent_results=None):
        """
        Orchestrates the analysis flow:
        1. Data preparation & Context injection
        2. Prompt formatting
        3. LLM Inference
        4. JSON Parsing & Validation
        """

        # 1. Context Preparation
        # We limit context to save tokens and focus on recent market trends
        market_sample = []
        if recent_results:
            for car in recent_results[:5]:
                market_sample.append(f"{car.get('title')} | {car.get('price')} EUR | {car.get('year')}")
        
        market_context_str = json.dumps(market_sample) if market_sample else "No market data available."

        # 2. Prompt Formatting
        # Injecting variables into the loaded text template
        prompt = self.prompt_template.format(
            description=description,
            price=price,
            mileage=mileage,
            year=year,
            market_context=market_context_str
        )

        # 3. LLM Call
        # Using the shared utility for API communication
        response_text = call_gemini(prompt)

        # 4. JSON Parsing & Validation (Wform week 3)
        # Robust parsing strategy to handle potential Markdown formatting in LLM response
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback in case of parsing failure
            print(f"JSON Parsing Error. Raw response: {response_text}")
            return {
                "price_position": "Unknown",
                "suggested_discount_eur": 0,
                "justification": "Automated analysis failed due to output format error.",
                "scam_risk_score": 0,
                "scam_reasons": [],
                "buyer_message": "Olá, vi o anúncio e tenho interesse. O preço é negociável?"
            }