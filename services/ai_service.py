"""
AI Service - All Gemini API interactions
Handles structured extraction, chat, and AI-powered analysis.
"""
import os
import json
from google import genai
from google.genai import types
from langfuse import observe
from utils.prompts import PromptLoader


class AIService:
    """Service for all AI operations using Gemini."""

    def __init__(self, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize AI service.

        Args:
            model: Gemini model to use (default: gemini-2.5-flash-lite)
        """
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = model
        self.prompts = PromptLoader()

    @observe(as_type="generation")
    def classify_ticket(self, ticket_text: str) -> dict:
        """
        Extract structured information from a support ticket.

        Args:
            ticket_text: Raw ticket text from customer

        Returns:
            Dictionary with extracted ticket information:
            - category: Support category
            - urgency: Priority level
            - customer_name: Extracted name if present
            - issue_summary: Brief description
        """
        schema = {
            "category": "string - one of: Authentication, Billing, Technical, Account Management, Sales, Data Recovery, General Support",
            "urgency": "string - one of: critical, high, medium, low",
            "customer_name": "string - customer name if mentioned, otherwise 'Not specified'",
            "issue_summary": "string - one sentence summary of the issue"
        }

        # Load prompt from file and format with variables
        prompt = self.prompts.format(
            "classify_ticket",
            ticket_text=ticket_text,
            schema=json.dumps(schema, indent=2)
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for consistent classification
                response_mime_type='application/json'
            )
        )

        return json.loads(response.text)

    @observe(as_type="generation")
    def suggest_response(self, ticket_data: dict, context: str = None) -> str:
        """
        Generate a suggested response for the ticket.

        Args:
            ticket_data: Classified ticket information
            context: Optional context (similar tickets, knowledge base, etc.)

        Returns:
            Suggested response text
        """
        # Load system instruction from file
        system_instruction = self.prompts.load("suggest_response_system")

        # Format context section
        context_section = ""
        if context:
            context_section = f"\n\nRELEVANT CONTEXT:\n{context}"

        # Load and format user prompt from file
        user_prompt = self.prompts.format(
            "suggest_response_user",
            category=ticket_data['category'],
            urgency=ticket_data['urgency'],
            customer_name=ticket_data.get('customer_name', 'valued customer'),
            issue_summary=ticket_data['issue_summary'],
            sla_deadline=ticket_data.get('sla_deadline', 'Standard response time'),
            route_to=ticket_data.get('route_to', 'Support Team'),
            original_text=ticket_data.get('original_text', ''),
            context=context_section
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,  # Slightly higher for more natural responses
                system_instruction=system_instruction
            )
        )

        return response.text

    @observe(as_type="generation")
    def answer_question(self, question: str, ticket_context: dict) -> str:
        """
        Answer questions about a specific ticket using chat.

        Args:
            question: User's question
            ticket_context: Ticket information for context

        Returns:
            Answer to the question
        """
        # Load and format system instruction from file
        system_instruction = self.prompts.format(
            "answer_question_system",
            category=ticket_context['category'],
            urgency=ticket_context['urgency'],
            customer_name=ticket_context.get('customer_name', 'Not specified'),
            issue_summary=ticket_context['issue_summary'],
            sla_deadline=ticket_context.get('sla_deadline', 'Not calculated'),
            route_to=ticket_context.get('route_to', 'Not determined')
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=question,
            config=types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=system_instruction
            )
        )

        return response.text
