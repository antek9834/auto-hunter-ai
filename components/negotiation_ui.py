
import streamlit as st

def render_negotiation_analysis(data: dict):
    """
    Beautiful UI block for negotiation + scam check.
    """

    scam_score = data.get("scam_risk_score", 50)

    # COLORS LOGIC
    if scam_score < 30:
        color = "green"
        label = "LOW RISK"
        box = st.success
    elif scam_score < 70:
        color = "orange"
        label = "MEDIUM RISK"
        box = st.warning
    else:
        color = "red"
        label = "HIGH RISK — POSSIBLE SCAM"
        box = st.error

    # HEADER
    st.markdown(f"""
        <h2 style='color:{color}; margin-bottom:0;'>
            🚨 Offer Risk Score: {scam_score}/100
        </h2>
        <p style='color:{color}; font-size:18px; margin-top:0;'>
            {label}
        </p>
        """, unsafe_allow_html=True)

    box(f"Scam Risk Level: **{scam_score}/100**")

    # PRICE TABLE
    st.subheader("📊 Price Evaluation")

    st.table({
        "Field": [
            "Price Position",
            "Suggested Discount",
            "Estimated Final Price"
        ],
        "Value": [
            data.get("price_position", "N/A"),
            f"-{data.get('suggested_discount_eur', 0)} €",
            f"{3500 - data.get('suggested_discount_eur', 0)} €"
        ]
    })

    # JUSTIFICATION
    st.subheader("📝 Justification")
    st.write(data.get("justification", "No justification provided."))

    # SCAM REASONS
    st.subheader("🔍 Risk Factors")
    for r in data.get("scam_reasons", []):
        st.markdown(f"• {r}")

    # MESSAGE
    st.subheader("💬 Suggested Message to Seller")
    st.code(data.get("buyer_message", ""), language="text")
