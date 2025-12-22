Auto Hunter: AI-Powered Car Search & Analysis Agent

Academic Capstone Project | 2025/2026

Important Note on Observability:
This project currently has a specific dependency constraint with Langfuse. To ensure tracing functionality operates correctly, you must use Langfuse version 2.6.0 (pip install langfuse==2.60.0). Newer versions may introduce compatibility issues with the current implementation.

Auto Hunter is an intelligent automotive assistant designed to simplify the used car buying process. It combines real-time data scraping, Large Language Model (LLM) reasoning, and Retrieval-Augmented Generation (RAG) to provide a unified platform for searching, analyzing, and negotiating vehicle purchases in the Portuguese market.

Summary:

Buying a used car involves navigating fragmented data, assessing fair market value, and detecting potential fraud. Auto Hunter addresses these challenges by acting as a personalized agent that can:

Parse natural language intents into structured search queries.

Scrape live market data from Standvirtual using a headless browser.

Synthesize findings into ranked recommendations with AI-generated justifications.

Ingest external documents (e.g., VIN reports, insurance policies) to provide context-aware advice.

Evaluate individual offers for price fairness and scam indicators.

Key Features:

1. Intelligent Search & Ranking

Natural Language Processing: Users input queries like "Diesel BMW 3 Series under 20k with less than 100k km."

Structured Parsing: The system extracts key filters (Brand, Model, Fuel, Year, Price, KM) using Gemini.

Live Scraping: A custom Selenium scraper retrieves real-time listings from Standvirtual.

AI Re-Ranking: Results are sent back to the LLM to be ranked by relevance and annotated with a specific "Reason to Buy."

2. Chat About Cars

Interactive Chat: Users can chat directly with the AI about the scraped car listings, asking for comparisons, value assessments, or specific details about the vehicles found.

Contextual History: The chat retains context of the search results to answer follow-up questions intelligently.

3. Offer Negotiation Helper

Scam Detection: Analyzes listing descriptions for red flags (e.g., urgency, weird payment methods) and assigns a risk score.

Price Valuation: Compares the offer price against recent market data.

Message Generation: Drafts a culturally appropriate negotiation message in Portuguese to send to the seller.

4. Fuel & Cost Analyzer

Calculates monthly ownership costs based on user inputs (mileage, fuel price).

Provides AI-generated tips for reducing consumption based on specific driving habits.

5. Inspect Documents

Document Inspector: Use the "Document Inspector" feature to upload car‑related PDFs (like VIN reports or insurance policies).

Integrated Analysis: Combine the extracted document data with search results and chat to make a more informed decision.

Usage Guide:

This application is designed to be intuitive. Follow these steps to get the most out of it:

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

The AI will evaluate if the price is fair, detect potential scam risks (Red/Yellow/Green indicators), suggest a discount amount, and even write a negotiation message in Portuguese for you to send.

📄 Step 5: Inspect Documents

Deep Audit: Analyzes uploaded PDFs (like VIN reports or maintenance logs) specifically against the car's price and mileage.

Red Flag Detection: Automatically flags inconsistencies or risks found in the document text.

Verdict: Provides a structured "Go/No-Go" recommendation based on the document evidence.

Prerequisites:

Python 3.10+ with necessary packages

API Keys: Google Gemini, Langfuse (optional for tracing)

Installation Steps:

Clone the Repository

git clone <repo-url>
cd carsearch_ai


Install Dependencies:

Install all necessary Python packages for the project (such as streamlit, selenium, google-generativeai etc.).

Note: Ensure you explicitly install Langfuse version 2.6.0 (pip install langfuse==2.60.0) to avoid compatibility issues.

Environment Configuration
Create a .env file in the root directory:

GOOGLE_API_KEY="your_gemini_api_key"
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="[https://cloud.langfuse.com](https://cloud.langfuse.com)"


Get a Gemini API key here: https://aistudio.google.com/apikey

Run the Application:

streamlit run app.py
