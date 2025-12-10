import streamlit as st
from services.document_analyzer_service import DocumentAnalyzerService
# Safe import for flushing traces
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None

def render_document_tab():
    # Initialize service specifically for this tab
    if "doc_service" not in st.session_state:
        st.session_state.doc_service = DocumentAnalyzerService()

    st.header("📄 Document Inspector")
    st.markdown("Upload a **VIN document**, **Inspection Sheet (IPO)**, or **Invoice**. AI will analyze it for risks.")

    # Input Section
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Target Price (€)", min_value=0, value=0, step=500)
    with col2:
        mileage = st.number_input("Claimed Mileage (km)", min_value=0, value=0, step=1000)

    # File Uploader
    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "png", "jpg", "jpeg", "webp"])

    if st.button("🕵️ Analyze Document", type="primary"):
        if not uploaded_file:
            st.warning("Please upload a file first.")
            return

        with st.spinner("AI is reading and analyzing the document..."):
            # Call the service
            result = st.session_state.doc_service.analyze(uploaded_file, price, mileage)
            
            # Flush traces if using Langfuse
            if Langfuse:
                Langfuse().flush()

        # Error Handling
        if "error" in result:
            st.error(result["error"])
        else:
            st.divider()
            
            # --- Visual Result Display ---
            c1, c2 = st.columns([1, 2])
            with c1:
                #st.info(f"🚗 **{result.get('vehicle_identity', 'Unknown')}**")
                #st.metric("Price Verdict", result.get('price_verdict', 'N/A'))
                st.markdown("**Price Verdict:**")
                st.markdown(f"#### {result.get('price_verdict', 'N/A')}")
            
            with c2:
                st.subheader("Analysis Summary")
                st.write(result.get('summary'))
                st.write(f"**Consistency Check:** {result.get('consistency_check')}")

            # Red Flags
            if result.get('red_flags'):
                st.error("⚠️ Red Flags Detected:")
                for flag in result['red_flags']:
                    st.markdown(f"- {flag}")
            else:
                st.success("✅ No obvious red flags detected.")
            
            # Recommendation
            st.success(f"💡 **Recommendation:** {result.get('recommendation')}")
            
            # Debug: Show raw if parsing failed
            if result.get("raw_response"):
                with st.expander("Debug Raw Output"):
                    st.text(result["raw_response"])