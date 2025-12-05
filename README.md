# 🎫 HelpDesk AI

**Starter template** demonstrating clean architecture and integration of course concepts (Weeks 1-8).

> **Note**: This is a learning template built during Week 9's live coding session. It provides a foundation for understanding how AI concepts integrate, not a production-ready application.

## What This Template Demonstrates

This starter template shows how to:
- 📊 **Classify** support tickets by category and urgency using structured AI outputs
- ⏰ **Calculate** SLA deadlines based on priority using function calling tools
- 🎯 **Route** tickets to appropriate teams with business logic
- 💬 **Generate** suggested responses using AI prompting patterns
- 🔍 **Enable** natural language Q&A about tickets with chat sessions

## Course Concepts Demonstrated

| Week | Concept | Where to Find It |
|------|---------|------------------|
| 1 | Environment setup, dependencies | `.env`, `pyproject.toml` |
| 2 | API calls, chat sessions | `services/ai_service.py` |
| 3 | Structured outputs, prompting | `ai_service.classify_ticket()`, `prompts/*.txt` |
| 4 | Document processing | (Extensible for email/PDF tickets) |
| 5 | Function calling | `tools/sla_calculator.py`, `tools/business_hours.py` |
| 6 | Streamlit UI | `app.py` |
| 7 | Langfuse tracing | `@observe()` decorators throughout |
| 8 | Clean architecture | Service layers, prompt separation, `utils/prompts.py` |

## Project Structure

```
helpdesk_ai/
├── app.py                          # Streamlit UI (Week 6)
├── .env.example                    # Environment template
├── pyproject.toml                  # Dependencies (uv)
│
├── prompts/                        # AI prompt templates (Week 8)
│   ├── README.md                   # Prompt documentation
│   ├── classify_ticket.txt         # Classification prompt
│   ├── suggest_response_system.txt # Response generation (system)
│   ├── suggest_response_user.txt   # Response generation (user)
│   └── answer_question_system.txt  # Chat Q&A prompt
│
├── services/                       # Business logic layer
│   ├── ai_service.py               # All Gemini API calls (Week 2-3)
│   └── ticket_service.py           # Main orchestration
│
├── tools/                          # Function calling tools (Week 5)
│   ├── sla_calculator.py           # Calculate SLA deadlines
│   └── business_hours.py           # Business hours checking
│
└── utils/                          # Shared utilities
    ├── prompts.py                  # Prompt loader utility
    └── tracing.py                  # Langfuse configuration (Week 7)
```

## Setup Instructions

### 1. Clone and Navigate

```bash
cd Week_9/helpdesk_ai
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key at: https://aistudio.google.com/apikey

### 4. (Optional) Configure Langfuse Tracing

For observability, add Langfuse keys to `.env`:
```
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

Sign up at: https://cloud.langfuse.com

**Note:** The app works without Langfuse, but you won't see traces.

### 5. Run the App

```bash
uv run streamlit run app.py
```

Or:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### Analyze a Ticket

1. Go to the "📝 Analyze Ticket" tab
2. Either:
   - Click a sample ticket button, OR
   - Paste your own ticket text
3. Click "🔍 Analyze Ticket"
4. View the analysis:
   - Urgency level (Critical/High/Medium/Low)
   - Category (Authentication, Billing, etc.)
   - SLA deadline
   - Routing team
   - Suggested response

### Chat About a Ticket

1. After analyzing a ticket, go to "💬 Chat About Ticket" tab
2. Ask questions like:
   - "What team should handle this?"
   - "How urgent is this issue?"
   - "What are the next steps?"
3. Get AI-powered answers based on the ticket context

## Architecture Highlights

### Clean Separation of Concerns (Week 8)

**UI Layer** (`app.py`):
- Only handles display and user interaction
- No business logic
- Calls service methods

**Service Layer** (`services/`):
- Contains all business logic
- Orchestrates AI and tools
- Testable without UI

**AI Layer** (`services/ai_service.py`):
- All Gemini API interactions
- Loads prompts from `prompts/` directory
- Isolated from business logic
- Easy to swap models

**Prompts Layer** (`prompts/`):
- Separate prompt templates from code
- Easy to edit and iterate
- Version controlled independently
- Non-developers can modify

**Tools Layer** (`tools/`):
- Pure functions for calculations
- Can be used as function calling tools
- Independently testable

### Observable (Week 7)

Every function decorated with `@observe()`:
- View in Langfuse dashboard
- See full execution trace
- Debug production issues
- Track performance

## Sample Tickets

The app includes sample tickets you can try:

**Critical:**
> I can't log into my account. It keeps saying my password is invalid even though I'm sure it's correct. I've tried resetting it twice but the email never arrives. This is urgent!

**Medium:**
> The dashboard is loading very slowly, taking 30+ seconds. This started happening this morning.

Or try the `../sample_data/tickets.json` file for 30 realistic examples!

## Extending the App

This architecture makes it easy to add features:

### Edit Prompts (No Code Changes!)
```bash
# Just edit the text files in prompts/
# Restart the app - that's it!
nano prompts/classify_ticket.txt
uv run streamlit run app.py
```

See `prompts/README.md` for detailed prompt engineering guide.

### Add Email Parsing (Week 4)
```python
# services/email_service.py
def parse_email(email_file):
    # Extract text from email
    # Return ticket text
```

### Add Analytics
```python
# services/analytics_service.py
def get_ticket_stats():
    # Category distribution
    # Average response time
    # Team workload
```

### Add Multi-language Support
```python
# services/ai_service.py
def detect_language(text):
    # Detect customer language
    # Respond in same language
```

## Adapting for Your Project

This structure works for many domains:

**Legal:** Tickets → Case requests
```python
class CaseService:
    def process_case(self, case_text):
        # Classify legal case
        # Calculate filing deadlines
        # Route to legal team
```

**Medical:** Tickets → Patient queries
```python
class PatientQueryService:
    def process_query(self, query_text):
        # Classify medical query
        # Determine urgency
        # Route to specialist
```

**Academic:** Tickets → Student questions
```python
class StudentQuestionService:
    def process_question(self, question_text):
        # Classify by subject
        # Determine complexity
        # Route to TA/professor
```

## Common Issues

### "GOOGLE_API_KEY not found"
- Make sure you created `.env` file
- Check the key is correctly copied
- No spaces or quotes around the key

### "Langfuse tracing not configured"
- This is just a warning
- App works without Langfuse
- Add Langfuse keys if you want tracing

### Import Errors
- Make sure you're in the `helpdesk_ai/` directory
- Run `uv sync` to install dependencies
- Check Python version is 3.11+

## Learn More

- **Google Gemini:** https://ai.google.dev/
- **Streamlit:** https://docs.streamlit.io/
- **Langfuse:** https://langfuse.com/docs
- **UV Package Manager:** https://docs.astral.sh/uv/

## License

Educational use - Week 9 Integration Workshop
