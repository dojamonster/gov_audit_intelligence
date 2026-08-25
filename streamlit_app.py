import streamlit as st
import pandas as pd
import requests
from pypdf import PdfReader

st.set_page_config(
    page_title="Government Audit Intelligence", page_icon="🏛️", layout="centered"
)

df = pd.read_csv("audit_data.csv")

st.title("🏛️ Government Audit Intelligence Platform")
st.write("AI-Based Contractor Risk and Anomaly Analysis")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Contractors", len(df))

with col2:
    st.metric("High Risk Cases", (df["severity"] == "HIGH").sum())

with col3:
    st.metric("Low Risk Cases", (df["severity"] == "LOW").sum())

st.subheader("Audit Data")
st.dataframe(df, use_container_width=True)

st.subheader("Contractor Search")

search_id = st.text_input("Enter Contractor ID", key="contractor_search")

if search_id:
    search_result = df[df["contractor_id"].astype(str).str.upper() == search_id.upper()]
    st.dataframe(search_result, use_container_width=True)

st.subheader("Risk Filter")

risk_filter = st.selectbox(
    "Select Risk Level", ["ALL", "HIGH", "LOW"], key="risk_filter"
)

if risk_filter == "HIGH":
    filtered_df = df[df["severity"] == "HIGH"]
elif risk_filter == "LOW":
    filtered_df = df[df["severity"] == "LOW"]
else:
    filtered_df = df

st.dataframe(filtered_df, use_container_width=True)

st.subheader("Risk Score Overview")

score_data = pd.DataFrame(
    {"Risk Level": ["LOW", "HIGH", "CRITICAL"], "Risk Score": [30, 70, 100]}
)

st.bar_chart(score_data.set_index("Risk Level"))

st.subheader("Analysis History")

if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No contractor analysis performed yet.")

st.divider()

st.subheader("Contractor Details")

contractor_id = st.text_input("Contractor ID", key="analysis_contractor_id")

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

                st.session_state.history.append(result)

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

st.divider()

st.subheader("CAG Audit Report")

uploaded_file = st.file_uploader(
    "Upload CAG Audit Report PDF", type=["pdf"], key="cag_report_upload"
)

text = ""

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    st.success("PDF uploaded successfully.")

    st.subheader("Extracted Report Text")

    if text:
        st.text_area("Report Content", text[:10000], height=400)
    else:
        st.warning("No readable text found in this PDF.")

if uploaded_file is not None and text:
    st.subheader("Important Audit Findings")

    keywords = [
        "irregularity",
        "irregularities",
        "misappropriation",
        "loss",
        "shortage",
        "delay",
        "non-compliance",
        "non compliance",
        "excess payment",
        "fraud",
        "unutilized",
        "irregular expenditure",
    ]

    sentences = text.replace("\n", " ").split(".")
    findings = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        for keyword in keywords:
            if keyword in sentence_lower:
                findings.append(sentence.strip())
                break

    if findings:
        for i, finding in enumerate(findings[:20], 1):
            st.write(f"{i}. {finding}")
    else:
        st.info("No important findings detected.")
