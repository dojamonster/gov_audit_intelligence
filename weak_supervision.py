import pandas as pd

df = pd.read_csv("audit_findings.csv")

high_keywords = [
    "fraud",
    "misappropriation",
    "excess payment",
    "irregular expenditure",
    "major delay",
    "significant delay",
    "repeated issues",
    "loss",
    "shortage"
]

low_keywords = [
    "minor delay",
    "minor compliance",
    "no major irregularity",
    "completed with minor delay"
]

def assign_label(text):
    text = text.lower()

    high_score = sum(keyword in text for keyword in high_keywords)
    low_score = sum(keyword in text for keyword in low_keywords)

    if high_score > low_score and high_score > 0:
        return "HIGH"

    if low_score > high_score and low_score > 0:
        return "LOW"

    return "UNKNOWN"

df["predicted_severity"] = df["finding_text"].apply(assign_label)

print(df[[
    "finding_id",
    "contractor_id",
    "finding_text",
    "severity",
    "predicted_severity"
]])
