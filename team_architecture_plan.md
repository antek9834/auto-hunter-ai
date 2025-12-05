# Team Project Architecture Plan

**Team Name:** 

**Project Name:** _________________________

**Team Members:**
1. _________________________
2. _________________________
3. _________________________
4. _________________________

**Project Domain:** ☐ Legal  ☐ Medical  ☐ Academic  ☐ Business  ☐ Other: __________

---

## Part 1: Project Overview

### What problem are you solving?




### Who will use your application?




### What's your core value proposition? (In one sentence)




---

## Part 2: Define Your Layers

### UI Layer (Streamlit)

**What pages/screens do you need?**

1. Main page: _________________________
   - Purpose: _________________________

2. Additional page: _________________________
   - Purpose: _________________________

3. Additional page: _________________________
   - Purpose: _________________________

**User Inputs:**

- ☐ File upload (PDF, images, CSV, etc.)
  - File types: _________________________
- ☐ Text input (questions, search, forms)
  - For: _________________________
- ☐ Dropdown selections
  - Options: _________________________
- ☐ Sliders/numeric inputs
  - For: _________________________
- ☐ Other: _________________________

**What do you display to users?**

- ☐ Extracted structured data
- ☐ Chat conversations
- ☐ Charts/visualizations
- ☐ Tables
- ☐ Metrics/statistics
- ☐ Other: _________________________

---

### Service Layer (Business Logic)

**What services does your domain need?**

Think about major features/capabilities.

**Service 1:** _________________________ Service

Purpose: _________________________

Main responsibilities:
-
-
-

**Service 2:** _________________________ Service

Purpose: _________________________

Main responsibilities:
-
-
-

**Service 3:** _________________________ Service

Purpose: _________________________

Main responsibilities:
-
-
-

---

### AI Layer (Gemini Operations)

**What AI operations do you need?**

Check all that apply and describe:

- ☐ **Extract structured data from documents**
  - Extract what fields: _________________________

- ☐ **Chat/Q&A with context**
  - About what: _________________________

- ☐ **Summarization**
  - Summarize what: _________________________

- ☐ **Classification/Categorization**
  - Classify what into what categories: _________________________

- ☐ **Text generation**
  - Generate what: _________________________

- ☐ **Comparison**
  - Compare what: _________________________

- ☐ **Analysis**
  - Analyze what: _________________________

- ☐ **Other:** _________________________

**Will you need multi-turn conversations?**

☐ Yes
☐ No

If yes, for what purpose: _________________________

---

### Tools Layer (Function Calling)

**What calculations or actions does AI need help with?**

Think about things AI shouldn't do (precise math, dates, lookups).

**Tool 1:** _________________________

- Purpose: _________________________
- Inputs: _________________________
- Output: _________________________

**Tool 2:** _________________________

- Purpose: _________________________
- Inputs: _________________________
- Output: _________________________

**Tool 3:** _________________________

- Purpose: _________________________
- Inputs: _________________________
- Output: _________________________

**Will AI call these automatically?**

☐ Yes, using function calling
☐ No, services will call them directly

---

## Part 3: Data Flow

**Map your primary workflow:**

Choose your most important user action and trace it through the system.

**User Action:** _________________________

(e.g., "User uploads medical record and asks 'What medications am I taking?'")

**Step-by-Step Flow:**

```
1. User does: _________________________
        ↓
2. Streamlit (app.py) calls: _________________________
        ↓
3. Which service: _________________________
   What does it do:
   a. _________________________
   b. _________________________
   c. _________________________
        ↓
4. AI Service called for: _________________________
   Input: _________________________
   Output: _________________________
        ↓
5. Tools called: _________________________
   For: _________________________
        ↓
6. Data returned to UI: _________________________
        ↓
7. User sees: _________________________
```

**Draw a diagram on paper/whiteboard showing this flow!**

---

## Part 4: Data Schema

### What structured data do you extract?

**Your Domain Schema:**

```json
{
  "field_name_1": "type and description",
  "field_name_2": "type and description",
  "field_name_3": ["list of what"],
  "nested_object": {
    "sub_field": "type"
  }
}
```

**Your Actual Schema:**

```json
{




}
```

**Required fields (must have):**
-
-
-

**Optional fields (nice to have):**
-
-

---

## Part 5: Team Roles

**Who builds what:**

**Member 1:** _____________ → Responsible for: _________________________

**Member 2:** _____________ → Responsible for: _________________________

**Member 3:** _____________ → Responsible for: _________________________

---

## Part 6: Next Steps

**This week:**
- Set up project structure
- Create main service
- Test AI operations

**Next 2 weeks:**
- Build Streamlit UI
- Connect services
- Add tracing with Langfuse

**Final weeks:**
- Polish and improve UX
- Test thoroughly
- Deploy to Streamlit Cloud
- Prepare presentation

---

**This is your roadmap. Start building and adjust as you learn!**
