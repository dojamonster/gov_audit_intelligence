import pandas as pd
from email.message import EmailMessage

audit_df = pd.read_csv("audit_data.csv")
anomaly_df = pd.read_csv("temporal_anomaly_results.csv")

high_risk = audit_df[audit_df["severity"] == "HIGH"]
anomalies = anomaly_df[anomaly_df["anomaly_status"] == "ANOMALY"]

risk_data = anomaly_df.copy()

risk_data["risk_score"] = 30

risk_data.loc[
    (risk_data["severity"] == "HIGH") | (risk_data["anomaly_status"] == "ANOMALY"),
    "risk_score",
] = 70

risk_data.loc[
    (risk_data["severity"] == "HIGH") & (risk_data["anomaly_status"] == "ANOMALY"),
    "risk_score",
] = 100

top_risk = risk_data.sort_values("risk_score", ascending=False).iloc[0]

message = EmailMessage()

message["Subject"] = "Weekly Government Audit Risk Tip Sheet"
message["From"] = "audit-platform@example.com"
message["To"] = "audit-team@example.com"

body = f"""
Government Audit Intelligence Platform

WEEKLY AUDIT TIP SHEET

High Risk Contractors: {len(high_risk)}
Anomalies Detected: {len(anomalies)}

TOP RISK CONTRACTOR

Contractor ID: {top_risk["contractor_id"]}
Severity: {top_risk["severity"]}
Anomaly: {top_risk["anomaly_status"]}
Exposure Score: {top_risk["exposure_score"]}
Risk Score: {top_risk["risk_score"]}

WEEKLY TIPS

1. Review high-risk contractors.
2. Investigate detected exposure anomalies.
3. Check contractors with previous audit issues.
4. Monitor delays and high-value contracts.

This email was generated automatically by the Government Audit Intelligence Platform.
"""

message.set_content(body)

with open("weekly_audit_email.eml", "wb") as file:
    file.write(bytes(message))

print("Weekly audit email generated successfully!")
