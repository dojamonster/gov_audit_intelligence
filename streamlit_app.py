from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier

FEATURES = ["amount_lakh", "delay_days", "previous_issues"]

st.set_page_config(
    page_title="Government Audit Intelligence", page_icon="🏛️", layout="centered"
)


@st.cache_resource
def load_models():
    df = pd.read_csv(Path(__file__).parent / "audit_data.csv")
    y = df["severity"].map({"LOW": 0, "HIGH": 1})
    xgb = XGBClassifier(n_estimators=100, max_depth=3,
                        learning_rate=0.1, random_state=42)
    xgb.fit(df[FEATURES], y)
    iso = IsolationForest(contamination=0.2, random_state=42).fit(df[FEATURES])
    return xgb, iso


xgb_model, iso_model = load_models()


def analyze(amount_lakh, delay_days, previous_issues):
    X = pd.DataFrame([[amount_lakh, delay_days, previous_issues]],
                     columns=FEATURES)
    severity = "HIGH" if xgb_model.predict(X)[0] == 1 else "LOW"
    anomaly = "YES" if iso_model.predict(X)[0] == -1 else "NO"
    if severity == "HIGH" and anomaly == "YES":
        return severity, anomaly, "CRITICAL", 100
    if severity == "HIGH" or anomaly == "YES":
        return severity, anomaly, "HIGH", 70
    return severity, anomaly, "LOW", 30


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

        severity, anomaly, risk, score = analyze(
            data["amount_lakh"], data["delay_days"], data["previous_issues"]
        )
        result = {
            "severity": severity,
            "anomaly": anomaly,
            "risk": risk,
            "risk_score": score,
        }

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