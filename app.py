import multiprocessing
from components.document_ui import render_document_tab

try:
    # Fix for Streamlit + Selenium/Multiprocessing on macOS/Linux
    multiprocessing.set_start_method("spawn", force=True)
except RuntimeError:
    pass

import streamlit as st
import base64
import os
import uuid  
from dotenv import load_dotenv

from services.car_search_system import CarSearchService
from utils.tracing import init_tracing
from services.fuel_cost_service import FuelCostAnalysisService
from utils.prompts import PromptLoader
from utils.ai import call_gemini
from services.offer_analysis_service import OfferAnalysisService
from components.negotiation_ui import render_negotiation_analysis
from langfuse.decorators import observe, langfuse_context
# --- 1. ADD IMPORT FOR FLUSHING ---
from langfuse import Langfuse

# Load env vars and init tracing
load_dotenv()
init_tracing()

# INITIALIZE CLIENT FOR FLUSHING 
# This client instance is needed specifically to call .flush()
langfuse = Langfuse()

st.set_page_config(
    page_title="Auto Hunter",
    page_icon="🚗",
    layout="wide"
)

# SETUP SESSION ID 
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Configure Langfuse to group traces by this user session
langfuse_context.update_current_trace(
    session_id=st.session_state.session_id,
    tags=["streamlit_app", "auto_hunter"]
)

# --- FUNCTION TO SET BACKGROUND IMAGE ---
def set_background(image_file):
    # (Check if file exists to prevent errors if missing)
    if not os.path.exists(image_file):
        return
    with open(image_file, "rb") as f:
        data = f.read()
    b64_encoded = base64.b64encode(data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

# CSS FOR "FLOATING CARD" UI 
st.markdown(
    """
    <style>
    /* Target the main container - Force Dark Glassmorphism */
    .block-container {
        background-color: rgba(15, 15, 15, 0.85); /* Darker background for contrast */
        border-radius: 25px;
        padding: 40px !important;
        max-width: 85% !important;
        margin-top: 30px;
        margin-bottom: 50px;
        margin-left: auto;
        margin-right: auto;
        backdrop-filter: blur(10px);            
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Force text inside the main container to be white */
    .block-container h1, 
    .block-container h2, 
    .block-container h3, 
    .block-container h4, 
    .block-container h5, 
    .block-container h6, 
    .block-container p, 
    .block-container li, 
    .block-container span, 
    .block-container label,
    .block-container div {
        color: #ffffff !important;
    }

    /* --- SIDEBAR STYLING --- */
    /* Force sidebar background to be almost black */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important; /* Almost black */
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Force Sidebar Text to be White */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* Fix Sidebar file uploader text */
    section[data-testid="stSidebar"] .stFileUploader label {
        color: #ffffff !important;
    }

    /* Fix Input Fields - Force Dark Background with White Text */
    /* This ensures readability regardless of the user's theme setting */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stNumberInput > div > div > input {
        color: #ffffff !important;           /* White Text */
        background-color: #333333 !important; /* Dark Grey Background */
        border: 1px solid #555555;
    }
    
    /* Fix Selectbox/Dropdowns */
    div[data-baseweb="select"] > div {
        background-color: #333333 !important;
        color: white !important;
    }
    
    /* Fix Buttons */
    .stButton > button {
        border: 1px solid white;
        color: white !important;
        background-color: transparent;
    }
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


current_folder = os.path.dirname(__file__)
image_path = os.path.join(current_folder, "background.jpg")
set_background(image_path)

# Initialize session state variables
if 'car_service' not in st.session_state:
    st.session_state.car_service = None
if 'pdf_context' not in st.session_state:
    st.session_state.pdf_context = ""
if 'search_summary' not in st.session_state:
    st.session_state.search_summary = ""
if 'current_results' not in st.session_state:
    st.session_state.current_results = []
if "offer_service" not in st.session_state:
    st.session_state.offer_service = OfferAnalysisService()

header_path = os.path.join(current_folder, "black_header.png")
try:
    st.image(header_path, use_column_width=True)
except Exception:
    st.title("🚗 CarSearch AI")

# TRACED FUNCTIONS
# We wrap the logic in functions decorated with @observe()

@observe(name="fuel_cost_analysis")
def run_fuel_analysis(km_month, consumption, fuel_price, person_weight, num_people):
    service = FuelCostAnalysisService()
    return service.analyze(
        km_month,
        consumption,
        fuel_price,
        avg_person_weight=person_weight if person_weight > 0 else None,
        num_people=num_people if num_people > 0 else None
    )

@observe(name="car_search")
def run_car_search(query, service):
    filters = service.parse_query(query)
    results = service.search_cars(filters)
    return results

@observe(name="offer_negotiation")
def run_offer_analysis(service, description, price, mileage, year, recent_results):
    return service.analyze(
        description=description,
        price=price,
        mileage=mileage,
        year=year,
        recent_results=recent_results
    )

# UI LOGIC 

def fuel_cost_page():
    st.title("⛽ Fuel & Cost Analyzer")
    km_month = st.number_input("Monthly distance (km)", min_value=0.0)
    consumption = st.number_input("Average fuel consumption (L/100km)", min_value=0.0)
    fuel_price = st.number_input("Fuel price per liter (€)", min_value=0.0)
    person_weight = st.number_input("Average passenger weight (optional)", min_value=0.0)
    num_people = st.number_input("Number of passengers (optional)", min_value=0)

    if st.button("Calculate Fuel Costs"):
        # Call the TRACED function
        results = run_fuel_analysis(km_month, consumption, fuel_price, person_weight, num_people)
        
        st.subheader("Fuel Cost Results")
        st.json(results)

        loader = PromptLoader()
        prompt = loader.format("fuel_analysis_prompt", data_json=str(results))
        explanation = call_gemini(prompt)
        st.subheader("AI Recommendations")
        st.write(explanation)
        
        # --- 3. FLUSH ---
        langfuse.flush()

# SIDEBAR
with st.sidebar:
    st.header("How to use the app")
    st.markdown("""
    🔍 Search Cars:
    Describe the car you want in natural language, including things like brand, model, fuel type, minimum year, maximum mileage, and price range.
    The app opens Standvirtual in the background, pulls live listings that match, and ranks the best deals for you with an AI summary.​

    💬 Chat About Results:
    Go to “Chat About Cars” after a search to ask follow‑up questions like “Which car is the best value?” or “Which one is cheapest to run?”.​
    The assistant answers using your search results.

    ⛽ Check Fuel Costs:
    In the “Fuel Cost Analyzer” tab, enter your monthly km, consumption, and fuel price to see estimated monthly costs and AI tips.​

    🤝 Negotiate an Offer:
    Open “Offer Negotiation Helper” and paste the full description of a specific listing plus its price, km, and year.​
    The app analyzes price fairness based on your recent search, flags scam risk, suggests a discount, and generates a negotiation message in Portuguese to send to the seller.​

    📄 Inspect Documents: ​
    Use “Document Inspector” to upload car-related documents (VIN document,  Inspection Sheet (IPO), etc.) to get detailed insights and make more informed decisions.
    """)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Search Cars",
    "💬 Chat About Cars",
    "⛽ Fuel & Cost Analyzer",
    "🤝 Negotiation Helper",
    "📄 Document Inspector"  
])

# TAB 3 - FUEL COST ANALYZER 
with tab3:
    fuel_cost_page()

# TAB 1 - SEARCH
with tab1:
    st.header("🔍Search for Cars")
    user_query = st.text_area(
        "Enter your requirement",
        placeholder="Example: 'Diesel BMW Series 3 from 2018, max 80k km, price between 20.000€ and 30.000€'",
        height=100,
        help="You can specify Brand, Model, Fuel Type, Minimum Year, Max KM, and Price Range."
    )

    if st.button("Search", type="primary"):
        if not user_query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Searching Market for the best cars!"):
                if st.session_state.car_service is None:
                    try:
                        st.session_state.car_service = CarSearchService()
                    except Exception as e:
                        st.error(f"Failed to initialize service: {e}")
                        st.stop()

                # Call the TRACED function
                raw_results = run_car_search(user_query, st.session_state.car_service)

                if raw_results:
                    with st.spinner("🤖 AI is analyzing and ranking deals..."):
                        try:
                            # Ensure rank_and_annotate is also decorated in your Service class for full tracing
                            processed_results = st.session_state.car_service.rank_and_annotate(user_query, raw_results)
                            st.session_state.current_results = processed_results
                        except AttributeError:
                            st.session_state.current_results = raw_results
                    
                    with st.spinner("Generating final market report..."):
                        try:
                            summary = st.session_state.car_service.summarize_results(
                                st.session_state.current_results,
                                context_text=st.session_state.pdf_context
                            )
                            st.session_state.search_summary = summary
                        except AttributeError:
                            st.session_state.search_summary = ""
                            
                    # --- 3. FLUSH ---
                    langfuse.flush()
                else:
                    st.session_state.current_results = []
                    st.warning("No cars found matching your query. Check the terminal for details.")

    if st.session_state.current_results:
        results = st.session_state.current_results
        st.divider()
        st.markdown("### 🎯 Best Matches (Ranked by AI)")
        st.success(f"Found {len(results)} listings based on your criteria.")

        for car in results:
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                with col1:
                    if car.get('image_url') and "http" in car['image_url']:
                        st.image(car['image_url'], use_column_width=True)
                    else:
                        st.caption("No Image Available")
                with col2:
                    st.subheader(car.get('title', 'No Title'))
                    # AI Description
                    if car.get('ai_description'):
                        st.info(f"🤖 **AI says:** {car['ai_description']}")
                    
                    st.markdown(
                        f"**Price:** €{car.get('price', 0):,} | "
                        f"**Year:** {car.get('year', 'N/A')} | "
                        f"**KM:** {car.get('km', 0):,} km | "
                        f"**Fuel:** {car.get('fuel', 'N/A')}"
                    )
                    
                    if car.get('link'):
                        st.markdown(f"[👉 View Full Listing]({car['link']})")

        if st.session_state.search_summary:
            st.divider()
            st.info(f"**📊 Market Overview:**\n\n{st.session_state.search_summary}")

# TAB 2 - CHAT 
with tab2:
    st.header("💬Chat About Results")
    if not st.session_state.current_results:
        st.info("Please perform a search in the 'Search Cars' tab first.")
    else:
        if st.session_state.pdf_context:
            st.caption("Answering using search results + uploaded document context")
        else:
            st.caption("Answering using search results only")

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

        q = st.chat_input("Ask questions (e.g., 'Which represents the best value?')")
        if q:
            st.session_state.chat_history.append({'role': 'user', 'content': q})
            
            # Lazy init service if needed (e.g. page refresh)
            if st.session_state.car_service is None:
                 st.session_state.car_service = CarSearchService()

            with st.spinner("Analyzing..."):
                ans = st.session_state.car_service.chat_about_results(
                    q,
                    st.session_state.current_results,
                    context_text=st.session_state.pdf_context
                )
            st.session_state.chat_history.append({'role': 'assistant', 'content': ans})
            

            langfuse.flush()
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

# TAB 4 - OFFER NEGOTIATION HELPER
with tab4:

    if "offer_service" not in st.session_state:
        st.session_state.offer_service = OfferAnalysisService()

    st.header("🤝 Offer Negotiation Helper")
    st.markdown(
        "Paste any car offer description and the app will:\n"
        "- Analyze price fairness based on your data and recent search results\n"
        "- Suggest a realistic discount\n"
        "- Detect scam risk\n"
        "- Write a message to negotiate in Portuguese\n"
    )

    # User Inputs 
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input(
            "Price (€)", min_value=0.0, max_value=10000000.0, step=100.0
        )
    with col2:
        mileage = st.slider(
            "Mileage (km)", min_value=0, max_value=1_000_000_000, step=1000, value=150000
        )
        year = st.slider(
            "Production Year", min_value=1900, max_value=2025, value=2015
        )

    car_description = st.text_area(
        "Paste the full description from the listing:",
        height=200,
        placeholder="Example: Honda Civic 1.4i S, 2001, 107,000 km..."
    )

    # RUN ANALYSIS
    if st.button("Analyze Offer", type="primary"):
        if not car_description.strip():
            st.warning("Please paste the listing description.")
            st.stop()

        with st.spinner("Analyzing the offer using AI..."):
            # Call the TRACED function
            analysis = run_offer_analysis(
                st.session_state.offer_service,
                car_description,
                price,
                mileage,
                year,
                st.session_state.get("current_results", [])
            )
            
            langfuse.flush()

        st.subheader("📊 Negotiation Analysis")
        
        # Safety check
        if not analysis:
            st.error("AI returned no analysis. Please try again.")
            st.stop()

        # SCAM RISK VISUALIZATION
        risk = analysis.get("scam_risk_score", 50)
        if risk < 30:
            color = "#2ecc71"  # green
            label = "Low Scam Risk"
        elif risk < 70:
            color = "#f1c40f"  # yellow
            label = "Medium Scam Risk"
        else:
            color = "#e74c3c"  # red
            label = "High Scam Risk"

        # DISPLAY RESULTS
        st.markdown(
            f"""
            <div style='padding: 12px; border-radius: 8px; background-color:{color}; color:white;'>
                <strong>Scam Risk:</strong> {label} ({risk}/100)
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("### 💸 Price Evaluation")
        st.write(f"**Price Position:** {analysis.get('price_position', 'No data')}")
        
        discount = analysis.get("suggested_discount_eur")
        if discount is None:
            discount = 0
        st.write(f"**Suggested Discount:** {discount} €")

        st.write("### 📝 Justification")
        st.write(analysis.get("justification", "No justification provided."))

        st.write("### 🚨 Scam Indicators")
        scam_list = analysis.get("scam_reasons", [])
        if scam_list:
            for reason in scam_list:
                st.markdown(f"- {reason}")
        else:
            st.write("No scam indicators found.")

        st.write("### 📩 Negotiation Message (PT)")
        st.code(analysis.get("buyer_message", "No message generated."), language="markdown")

with tab5:
    render_document_tab()

# Footer
st.divider()
# st.caption("Built with ❤️ using Streamlit | AutoHunter AI")
