import pandas as pd

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

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Weekly Audit Tip Sheet</title>
</head>
<body>
<h1>Government Audit Intelligence Platform</h1>
<h2>Weekly Audit Tip Sheet</h2>

<p><strong>High Risk Contractors:</strong> {len(high_risk)}</p>
<p><strong>Anomalies Detected:</strong> {len(anomalies)}</p>

<h3>Top Risk Contractor</h3>
<p><strong>Contractor ID:</strong> {top_risk["contractor_id"]}</p>
<p><strong>Severity:</strong> {top_risk["severity"]}</p>
<p><strong>Anomaly:</strong> {top_risk["anomaly_status"]}</p>
<p><strong>Exposure Score:</strong> {top_risk["exposure_score"]}</p>
<p><strong>Risk Score:</strong> {top_risk["risk_score"]}</p>

<h3>Key Tip</h3>
<p>Prioritize contractors with high severity and anomaly indicators for detailed audit review.</p>

<h3>Weekly Summary</h3>
<ul>
<li>Review high-risk contractors.</li>
<li>Investigate detected exposure anomalies.</li>
<li>Check contractors with previous audit issues.</li>
<li>Monitor delays and high-value contracts.</li>
</ul>

</body>
</html>
"""

with open("weekly_tip_sheet.html", "w", encoding="utf-8") as file:
    file.write(html)

print("Weekly Tip Sheet generated successfully!")
