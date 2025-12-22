## 🚗 Auto Hunter: AI-Powered Car Search & Analysis Agent

## Academic Capstone Project | AI Systems Engineering | 2025/2026

Important Note on Observability:
This project currently has a specific dependency constraint with Langfuse. To ensure tracing functionality operates correctly, you must use Langfuse version 2.6.0 (pip install langfuse==2.60.0). Newer versions may introduce compatibility issues with the current implementation.

## Overview

Auto Hunter is an intelligent automotive assistant designed to simplify the used car buying process. It combines real-time data scraping, Large Language Model (LLM) reasoning, and Retrieval-Augmented Generation (RAG) to provide a unified platform for searching, analyzing, and negotiating vehicle purchases in the Portuguese market.

Buying a used car involves navigating fragmented data, assessing fair market value, and detecting potential fraud. Auto Hunter addresses these challenges by acting as a personalized agent that can:

Parse natural language intents into structured search queries.

Scrape live market data from Standvirtual using a headless browser.

Synthesize findings into ranked recommendations with AI-generated justifications.

Ingest external documents (e.g., VIN reports, insurance policies) to provide context-aware advice.

Evaluate individual offers for price fairness and scam indicators.

Deployed app can be accessed on: https://auto-hunter-ai-12.streamlit.app/?brid=2DgJGdR9FkOcI4GZrAx22g

## Features

Intelligent Search & Ranking: Parses natural language queries (e.g., "Diesel BMW under 20k") into structured filters, scrapes live data from Standvirtual, and re-ranks listings with AI-generated "Reasons to Buy."

Chat About Cars: Allows users to upload PDF documents (insurance policies, mechanic checklists) and cross-reference them with search results via a chat interface.

Offer Negotiation Helper: Analyzes specific listing descriptions to detect scam risks (Red/Yellow/Green indicators), evaluates price fairness, and drafts culturally appropriate negotiation messages in Portuguese.

Fuel & Cost Analyzer: Calculates estimated monthly ownership costs based on user inputs and provides AI-generated tips for reducing consumption.

Document Inspector: A dedicated tool to audit vehicle documents like VIN reports or IPO sheets, providing an AI verdict on potential red flags.

## Tech Stack

Backend:

Python 3.10+

Google Gemini 2.5 Flash (via google-generativeai and REST API)

Frontend:

Streamlit

Data Retrieval:

Selenium WebDriver for scraping Standvirtual

AI/ML:

Langfuse for observability (latency, token usage tracking)

## Architecture

The Auto Hunter system follows a modular, service-oriented architecture:

Frontend (Streamlit): Handles user interactions, state management, and visualization. Key UI components like negotiation_ui.py and document_ui.py manage specific tabs.

Orchestrator (CarSearchService): Coordinates the flow between user input, the LLM parser, the scraper, and the ranking engine.

Intelligence Layer (utils/ai.py): A centralized wrapper for Google Gemini that handles prompts for parsing, reasoning, summarization, and chat.

Data Retrieval (StandvirtualScraper): A custom Selenium-based tool that navigates the Standvirtual website to extract real-time car data.

Logic Services: Dedicated services for specific tasks:

OfferAnalysisService: Logic for scam detection, price position, and negotiation drafts.

FuelCostService: Logic for fuel consumption calculations.

DocumentAnalyzerService: Logic for auditing uploaded PDFs against vehicle data.

## Installation & Setup

Prerequisites

Python 3.10+

Google Chrome (for Selenium)

API Keys: Google Gemini, Langfuse (optional for tracing)

Required Python Packages:

streamlit

selenium

beautifulsoup4

requests

pandas

python-dotenv

backoff

langfuse==2.60.0 (Note version constraint)

Installation Steps

Clone the repository:

git clone <repo-url> carsearch_ai
cd carsearch_ai


Install dependencies:

pip install (all necessary packages)
# Ensure you explicitly install the working version of Langfuse:
pip install langfuse==2.60.0


Set up environment variables:
Create a .env file in the root directory:

GOOGLE_API_KEY="your_gemini_api_key"
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="[https://cloud.langfuse.com](https://cloud.langfuse.com)"


Get a Gemini API key here: https://aistudio.google.com/apikey

Run the application:

streamlit run app.py


## Usage

🔍 Step 1: Search Cars

Navigate to the Search Cars tab. Describe the car you want in natural language in the text box.

Example: "I want a Fiat 500, petrol, after 2018, under 15000 euros."

Click Search. The app will open a browser in the background, fetch live listings from Standvirtual, and present them ranked by how well they match your needs.

💬 Step 2: Chat About Results

Once you have search results, switch to the Chat About Cars tab.

Ask follow‑up questions like: “Which of these cars is the best value?” or “Which one has the lowest mileage?”.

The AI assistant will analyze the specific listings found in Step 1 to give you a personalized answer.

⛽ Step 3: Check Fuel Costs

Go to the Fuel & Cost Analyzer tab to estimate ownership costs.

Enter your expected monthly mileage, the car's average consumption, and current fuel price.

The AI will calculate your estimated monthly fuel bill and provide tips on how to save money.

🤝 Step 4: Negotiate an Offer

Found a specific listing you like? Go to the Offer Negotiation Helper tab.

Paste the full description of the listing along with its price, mileage, and year.

Click Analyze Offer.

The AI will evaluate if the price is fair, detect potential scam risks, suggest a discount amount, and write a negotiation message in Portuguese.

📄 Step5: Inspect Documents

If you have external documents like a VIN Report, Insurance Policy, or Mechanic's Checklist:

Navigate to the Document Inspector tab.

Upload your PDF document to the analyzer.

The AI will review the document content, identifying potential red flags or important details to help you make an informed decision.

## Project Structure

<pre>
auto-hunter-ai/
├── app.py                         # Main entry point (Streamlit UI)
├── .env.example                   # Template for environment variables
├── services/                      # Business Logic Layer
│   ├── car_search_system.py       # Orchestrates search & RAG workflows
│   ├── document_analyzer_service.py # Document audit logic
│   ├── document_processor.py      # PDF text extraction
│   ├── fuel_cost_service.py       # Fuel consumption logic
│   └── offer_analysis_service.py  # Negotiation & risk assessment
├── tools/                         # External Interaction Layer
│   ├── standvirtual_scraper.py    # Selenium web scraper
│   └── fuel_tools.py              # Fuel calculation helpers
├── utils/                         # Shared Utilities
│   ├── ai.py                      # Centralized Gemini API wrapper
│   ├── tracing.py                 # Langfuse initialization
│   └── prompts.py                 # Prompt template management
├── prompts/                       # Raw Prompt Files
│   ├── car_query.txt              # Few-shot examples for search parsing
│   ├── document_analysis_prompt.txt # Instructions for PDF auditing
│   ├── fuel_analysis_prompt.txt   # Instructions for fuel cost insights
│   └── offer_analysis_prompt.txt  # Instructions for negotiation logic
└── components/                    # UI Components
    ├── document_ui.py             # UI for Document Inspector tab
    └── negotiation_ui.py          # UI for Negotiation tab

</pre>
## Team

- Antek - Architect, QA & Testing
- Jakub - Data Engineer
- Katarina - AI Engineer
- Nina - Frontend Developer

## License

Educational Use Only.
