# Prompts Directory

This directory contains all AI prompt templates used by HelpDesk AI.

## Why Separate Prompts?

**Benefits:**
- ✅ Easy to iterate and improve prompts without touching code
- ✅ Non-developers (product, support team) can edit prompts
- ✅ Version control friendly - track prompt changes separately
- ✅ A/B testing prompts is easier
- ✅ Reusable across different services
- ✅ Follows separation of concerns (Week 8 principle)

## Prompt Files

### `classify_ticket.txt`
**Purpose:** Extract structured data from support tickets
**Used by:** `AIService.classify_ticket()`
**Variables:** `{ticket_text}`, `{schema}`

### `suggest_response_system.txt`
**Purpose:** System instructions for email response generation
**Used by:** `AIService.suggest_response()`
**Variables:** None (static system prompt)

### `suggest_response_user.txt`
**Purpose:** User prompt for email response generation
**Used by:** `AIService.suggest_response()`
**Variables:** `{category}`, `{urgency}`, `{customer_name}`, `{issue_summary}`, `{sla_deadline}`, `{route_to}`, `{original_text}`, `{context}`

### `answer_question_system.txt`
**Purpose:** System instructions for ticket Q&A chat
**Used by:** `AIService.answer_question()`
**Variables:** `{category}`, `{urgency}`, `{customer_name}`, `{issue_summary}`, `{sla_deadline}`, `{route_to}`

## How to Use

### In Code:
```python
from utils.prompts import PromptLoader

# Initialize loader
prompts = PromptLoader()

# Load a prompt
prompt_text = prompts.load("classify_ticket")

# Load and format a prompt with variables
formatted_prompt = prompts.format(
    "classify_ticket",
    ticket_text="Customer cannot login",
    schema=json.dumps(schema)
)
```

### Editing Prompts:
1. Open the `.txt` file you want to edit
2. Make your changes
3. Save the file
4. Restart the app - changes take effect immediately!

## Prompt Engineering Tips

**For Classification:**
- Be explicit about categories and criteria
- Use bullet points and clear structure
- Include examples of edge cases
- Specify output format precisely

**For Response Generation:**
- Define clear structure (greeting, body, closing)
- Set tone guidelines
- Include brand voice (HelpDesk AI)
- Provide examples of good vs bad responses

**For Chat:**
- Give context about the ticket
- Set boundaries (what the AI should/shouldn't do)
- Be specific about information sources

## Testing Prompts

To test prompt changes:
1. Edit the prompt file
2. Run the app: `uv run streamlit run app.py`
3. Test with sample tickets
4. Check Langfuse dashboard for quality
5. Iterate!

## Version Control

When committing prompt changes:
- Use descriptive commit messages
- Explain WHY the change improves output
- Link to example tickets if possible
- Tag commits with `[prompts]` prefix

Example:
```bash
git commit -m "[prompts] Improve urgency classification for auth issues"
```
