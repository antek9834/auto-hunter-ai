# Architecture Documentation: Auto Hunter AI

This document provides a detailed overview of the architectural design, component responsibilities, and technical justifications for the **Auto Hunter AI** system.

---

## 1. Introduction
Auto Hunter AI is a web-based decision-support prototype designed to mitigate information asymmetry in the European used-car market. It empowers budget-conscious and first-time buyers by providing AI-driven search, real-time market analysis, and negotiation support. 

**Scope:** This system is developed as a Capstone Project for a Bachelor’s Degree in Data Science, focusing on modularity and AI integration rather than a full-scale commercial platform.

## 2. Architectural Style
The system follows a **client-server architecture** with a **layered backend design**. This approach ensures a clean separation between user interaction, business logic, and external AI services, allowing for better maintainability and the ability to swap models or data sources with minimal friction.

## 3. High-Level System Overview
The application is structured into four primary layers that interact with external dependencies:

* **UI Layer (Frontend):** Handles user inputs and displays results.
* **Service Layer (Orchestration):** Coordinates complex workflows like scraping and ranking.
* **AI Layer:** Manages all LLM-specific communication.
* **Tools Layer:** Provides specialized utilities for data extraction and calculation.
* **External Dependencies:** Includes Standvirtual.pt (data), Google Gemini API (intelligence), and Langfuse (observability).

## 4. Core Components

### 4.1 Frontend (UI Layer)
* **Technology:** Implemented entirely in **Streamlit** (`app.py`).
* **Responsibilities:**
    * Collecting natural language queries and file uploads (PDFs).
    * Maintaining session state for chat-based interactions.
    * Rendering color-coded visual warnings for scam risks and formatted negotiation messages.

### 4.2 Backend (Service Layer)
The Service Layer acts as the central orchestrator:
* **`CarSearchService`:** Translates free-text queries into filters, triggers scraping, and ranks results.
* **`OfferAnalysisService`:** Evaluates price fairness and detects scam risks in listing descriptions.
* **`FuelCostAnalysisService`:** Computes estimated ownership costs based on usage patterns.
* **`DocumentAnalyzerservice`:** Processes uploaded files and analyzes the car offer accordingly.

### 4.3 LLM Integration Layer (AI Layer)
* **Model:** **Google Gemini 2.5 Flash**.
* **Implementation:** All calls are encapsulated in `ai.py` to ensure the rest of the system never interacts with the API directly.
* **Output Strategy:** Uses strict **JSON schema enforcement** and Pydantic validation to ensure the LLM returns reliable, parsable data for backend processing.

### 4.4 Data Storage
* **Approach:** **Database-less design**.
* **Justification:** Real-time scraping of Standvirtual.pt guarantees up-to-date listing information, which is more valuable than stale historical data in a fluctuating market.

## 5. Request–Response Flow
The typical flow for a car search is as follows:
1.  **Input:** User submits a natural language request (e.g., "Diesel BMW under 20k").
2.  **Parsing:** The Service Layer sends the query to the AI Layer to extract structured filters.
3.  **Scraping:** `StandvirtualScraper` uses Selenium/BeautifulSoup to fetch live listings.
4.  **Ranking:** The AI Layer evaluates retrieved listings against the user's full intent.
5.  **Summarization:** Gemini generates a high-level market summary of the results.
6.  **Display:** The UI Layer renders the ranked cards and market analysis.

## 6. Prompt Engineering Strate
The `PromptLoader` module centralizes all templates. Strategies include:
* **System Instructions:** Defining the AI's role as a car search assistant.
* **Few-Shot Examples:** Providing input-output mappings to maximize model adherence to formats.
* **Strict Rules:** Instructions for inferring brands from models or converting shorthand text (e.g., "10k" to 10,000).

## 7. Non-Functional Requirements
* **Observability:** Integrated with **Langfuse** to trace latency, token usage, and AI reasoning paths.
* **Reliability:** Uses the `Backoff` library to automatically retry failed API calls due to rate limits.
* **Performance:** The Flash variant of Gemini is used to maintain a response time goal of under 7 seconds.

## 8. Design Decisions & Trade-offs
* **Manual Parsing vs. Function Calling:** Chosen to maintain full control over validation and avoid vendor-specific lock-in.
* **No User Accounts:** Omitted to focus development time on core AI features and search accuracy.
* **Manual VIN Uploads:** Implemented as a workaround for the lack of affordable, public VIN-check APIs.

## 9. Limitations
* **Scraping Risks:** External platforms may implement CAPTCHAs or rate limits that block data retrieval.
* **Latency:** Large prompt sizes for complex ranking tasks can introduce delays.
* **API Quotas:** Dependency on the free tier of Gemini can lead to temporary service interruptions (429 errors).

## 10. Future Improvements
* **Marketplace Expansion:** Integrating additional sources like OLX or mobile.de.
* **Computer Vision:** Implementing image-based car search and model detection.
* **Historical Tracking:** Implementing long-term price tracking once data storage is integrated.
