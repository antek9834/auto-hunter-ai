"""
Car Service - Main orchestration for car search and analysis
Coordinates AI query parsing, web scraping, summarization, and Q&A.
"""

from langfuse import observe
from services.car_search_system import CarSearchService

class CarService:
    """Service for processing and managing car searches."""

    def __init__(self):
        """Initialize car service with dependencies."""
        self.car_service = CarSearchService()

    @observe()
    def process_query(self, user_query: str) -> dict:
        """
        Complete car search pipeline.

        Orchestrates:
        1. Parse user query using LLM
        2. Search cars on Standvirtual
        3. Apply filters
        4. Return structured search results

        Args:
            user_query: Raw user query about cars

        Returns:
            Dict with parsed filters and search results
        """
        # Step 1: Parse query
        filters = self.car_service.parse_query(user_query)

        # Step 2: Search cars with parsed filters
        results = self.car_service.search_cars(filters)

        # Step 3: Summarize results
        summary = self.car_service.summarize_results(results)

        return {
            "filters": filters,
            "results": results,
            "summary": summary
        }

    @observe()
    def chat_about_results(self, question: str, current_results: list[dict]) -> str:
        """
        Answer user follow-up questions about the car search results.

        Args:
            question: User question
            current_results: List of current search results

        Returns:
            Answer to user's question
        """
        return self.car_service.chat_about_results(question, current_results)

    def get_supported_filters(self) -> list[str]:
        """
        Returns list of supported filter keys.

        Returns:
            List of strings: brand, model, max_price, min_year, max_km, fuel, location
        """
        return ["brand", "model", "max_price", "min_year", "max_km", "fuel", "location"]
