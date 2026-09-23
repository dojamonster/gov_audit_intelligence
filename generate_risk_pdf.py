import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

df = pd.read_csv("audit_data.csv")
anomaly_df = pd.read_csv("temporal_anomaly_results.csv")

contractor_id = "C008"

contractor = df[df["contractor_id"] == contractor_id].iloc[0]
anomaly = anomaly_df[anomaly_df["contractor_id"] == contractor_id].iloc[0]

amount_lakh = contractor["amount_lakh"]
delay_days = contractor["delay_days"]
previous_issues = contractor["previous_issues"]
severity = contractor["severity"]
audit_date = anomaly["audit_date"]
exposure_score = anomaly["exposure_score"]
anomaly_status = anomaly["anomaly_status"]

if severity == "HIGH" and anomaly_status == "ANOMALY":
    risk = "CRITICAL"
    risk_score = 100
elif severity == "HIGH" or anomaly_status == "ANOMALY":
    risk = "HIGH"
    risk_score = 70
else:
    risk = "LOW"
    risk_score = 30

pdf = SimpleDocTemplate("C008_risk_profile.pdf", pagesize=A4)

styles = getSampleStyleSheet()

story = []

story.append(Paragraph("Government Audit Intelligence Platform", styles["Title"]))
story.append(Spacer(1, 20))
story.append(Paragraph("Contractor Risk Profile", styles["Heading2"]))
story.append(Spacer(1, 15))

details = [
    f"Contractor ID: {contractor_id}",
    f"Audit Date: {audit_date}",
    f"Contract Amount: Rs. {amount_lakh} Lakh",
    f"Delay Days: {delay_days}",
    f"Previous Issues: {previous_issues}",
    f"Severity: {severity}",
    f"Anomaly: {anomaly_status}",
    f"Exposure Score: {exposure_score}",
    f"Risk: {risk}",
    f"Risk Score: {risk_score}",
]

for detail in details:
    story.append(Paragraph(detail, styles["BodyText"]))
    story.append(Spacer(1, 10))

pdf.build(story)

print("Risk profile PDF generated successfully!")
