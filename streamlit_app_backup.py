import streamlit as st
import requests

st.set_page_config(
    page_title="Government Audit Intelligence", page_icon="🏛️", layout="centered"
)

st.title("🏛️ Government Audit Intelligence Platform")
st.write("AI-Based Contractor Risk and Anomaly Analysis")

st.divider()

st.subheader("Contractor Details")

contractor_id = st.text_input("Contractor ID")

amount_lakh = st.number_input("Contract Amount (Lakh)", min_value=0.0, step=1.0)

delay_days = st.number_input("Delay Days", min_value=0, step=1)

previous_issues = st.number_input("Previous Issues", min_value=0, step=1)

if st.button("Analyze Contractor", use_container_width=True):
    if contractor_id == "":
        st.warning("Please enter Contractor ID")
    else:
        data = {
            "contractor_id": contractor_id,
            "amount_lakh": amount_lakh,
            "delay_days": delay_days,
            "previous_issues": previous_issues,
        }

        try:
            response = requests.post("http://127.0.0.1:8000/analyze", json=data)

            if response.status_code == 200:
                result = response.json()

                st.divider()
                st.subheader("Analysis Result")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Severity", result["severity"])
                    st.metric("Risk", result["risk"])

                with col2:
                    st.metric("Anomaly", result["anomaly"])
                    st.metric("Risk Score", result["risk_score"])

                st.success("Contractor analysis completed successfully.")

            else:
                st.error("FastAPI analysis failed.")

        except requests.exceptions.ConnectionError:
            st.error("FastAPI server is not running.")
