🚗 CarSearch AI

AI-powered automotive assistant combining intelligent scraping, market analysis, negotiation support and scam-risk detection.

Note: This project was developed for educational purposes.
It demonstrates AI integration, architecture design and Streamlit UI — not a production-grade system.

✨ What This Application Does

CarSearch AI allows users to:

🔍 Search car listings & parse structured data

🤖 Rank vehicles using AI reasoning

🧠 Chat about search results with contextual awareness

💸 Evaluate price fairness

🚨 Detect scam risk from listing description

🤝 Generate negotiation messages (PT)

⛽ Calculate fuel costs + AI explanation

📄 Read PDF guides/VIN reports for contextual analysis

🧩 Concepts Demonstrated
Area	Concept	Location
Environment	Setup, config	.env, pyproject.toml
AI	REST Gemini API wrapper	utils/ai.py
Prompt Engineering	Templates & formatting	prompts/*.txt
Business Logic	Modular services	services/*.py
Scraping	Standvirtual car extraction	car_search_system.py
ML Reasoning	AI ranking, analysis	offer_analysis_service.py
UI	Streamlit frontend	app.py
Architecture	Clean layering	services → utils → components
📁 Project Structure
carsearch_ai/
├── app.py                           # Streamlit UI (main entry point)
├── .env.example                     # Template for environment variables
├── pyproject.toml                   # Dependencies and project configuration
│
├── services/                        # Business logic layer
│   ├── car_search_system.py         # Scraping, ranking, summarisation
│   ├── fuel_cost_service.py         # Fuel cost computations
│   ├── offer_analysis_service.py    # Scam risk, pricing, negotiation logic
│
├── utils/                           # Shared utilities
│   ├── ai.py                        # Central Gemini API wrapper
│   ├── prompts.py                   # Prompt loader
│   └── tracing.py                   # Optional tracing
│
├── components/
│   └── negotiation_ui.py            # UI components for negotiation results
│
└── prompts/
    ├── search_prompt.txt
    ├── market_summary.txt
    └── negotiation_prompt.txt

⚙️ Setup Instructions
1. Clone the repository
git clone <repo-url>
cd carsearch_ai

2. Install dependencies

Using uv (recommended):

uv sync


Or using pip:

pip install -r requirements.txt

3. Configure environment variables

Copy template:

cp .env.example .env


Add your API key:

GOOGLE_API_KEY=your_key_here


Get one here → https://aistudio.google.com/apikey

4. Run the app

Using uv:

uv run streamlit run app.py


Or:

streamlit run app.py


The app launches at:
👉 http://localhost:8501

🧑‍💻 How to Use
🔍 Search Cars

Enter natural-language criteria

System scrapes listings

AI ranks them

Summary overview is provided

💬 Chat About Cars

Ask questions like:

"Which one is best value?"

"Is the mileage suspicious?"

"Compare the top 3."

AI answers using your current search + PDF context.

🤝 Negotiation Helper

Paste offer details → system returns:

Scam risk (green / yellow / red)

Price position

Discount suggestion

Full justification

Portuguese negotiation message

⛽ Fuel & Cost Analyzer

Input:

km/month

fuel consumption

fuel price

AI explains cost patterns and gives recommendations.

🔧 Architecture Details
UI Layer — app.py

Manages Streamlit pages

No business logic

Calls services only

Service Layer

Located in services/:

File	Responsibility
car_search_system.py	Scraping, ranking, summarising
offer_analysis_service.py	Scam detection, pricing logic
fuel_cost_service.py	Fuel cost computation
AI Layer — utils/ai.py

Contains central Gemini REST API wrapper

Allows changing model in one place

Handles errors & rate limits

Prompt Layer — prompts/*.txt

Editable without touching code

Clean separation

⚠️ Handling AI Quota Errors

During testing we encountered this error:

Gemini API error (429):
"You exceeded your current quota...
Quota exceeded for metric: generate_content_free_tier_requests
retryDelay: 54s"


To mitigate such issues, the app is structured so that:

All AI calls go through one wrapper → easy model swap

Fallback models can be introduced

Caching can reduce repeated calls

Centralized error handling prevents UI crashes

🚀 Future Improvements

Support for OLX, Autoscout24, mobile.de

Image recognition for car model detection

VIN API integrations (CarVertical, AutoDNA)

User logins & saved searches

Alerts for new listings

🛠️ Common Issues
"GOOGLE_API_KEY not found"

→ Ensure .env exists and contains your key.

Scraping returns empty data

→ Standvirtual may rate-limit; retry later.

429 quota exceeded

→ Free Gemini tier exhausted; wait or change model in ai.py.

📚 Learn More

Google Gemini → https://ai.google.dev

Streamlit → https://docs.streamlit.io

uv package manager → https://docs.astral.sh/uv

📄 License

Educational use — AI Systems Engineering Project (2024/2025)
