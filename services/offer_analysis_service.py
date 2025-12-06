import os
import json
from utils.ai import call_gemini

# Safe Import for Langfuse
try:
    from langfuse.decorators import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func): return func
        return decorator

class OfferAnalysisService:
    """
    Evaluates a car offer using LLM:
    - Price fairness
    - Discount recommendation
    - Scam risk
    - Negotiation message
    """

    def __init__(self):
        self.model = "gemini-2.5-flash-preview-09-2025"

    @observe(as_type="generation")
    def analyze(self, description, price, mileage, year, recent_results=None):
        """
        Uses Gemini to analyze a car offer.
        """

        # Prepare recent market data (optional)
        market_sample = []
        if recent_results:
            for car in recent_results[:8]:
                market_sample.append({
                    "title": car.get("title"),
                    "price": car.get("price"),
                    "year": car.get("year"),
                    "km": car.get("km")
                })

        prompt = f"""
You are a professional used-car market analyst.

Your task: Evaluate the offer and return a JSON object with:
- price_position (string)
- suggested_discount_eur (integer)
- justification (string)
- scam_risk_score (0–100)
- scam_reasons (array of strings)
- buyer_message (text in Portuguese)

CAR OFFER:
Description: {description}
Price: {price} €
Mileage: {mileage} km
Year: {year}

RECENT MARKET RESULTS (from user search):
{json.dumps(market_sample, indent=2)}

Now output JSON ONLY in this format:

{{
  "price_position": "...",
  "suggested_discount_eur": 0,
  "justification": "...",
  "scam_risk_score": 0,
  "scam_reasons": ["..."],
  "buyer_message": "..."
}}
"""

        # Call Gemini using existing helper
        llm_response = call_gemini(prompt)

        # LLM sometimes prints explanation before JSON → extract JSON safely
        try:
            start = llm_response.index("{")
            end = llm_response.rindex("}") + 1
            json_text = llm_response[start:end]
            data = json.loads(json_text)
            return data
        except Exception:
            return {
                "price_position": "Unable to determine.",
                "suggested_discount_eur": 0,
                "justification": f"AI returned invalid format: {llm_response[:100]}...",
                "scam_risk_score": 50,
                "scam_reasons": ["Could not parse AI output."],
                "buyer_message": "Desculpa — não consegui analisar a oferta."
            }