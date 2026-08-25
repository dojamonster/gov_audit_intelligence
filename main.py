from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest

app = FastAPI(
    title="Government Audit Intelligence Platform",
    description="API for CAG audit risk and anomaly analysis",
    version="1.0.0",
)

df = pd.read_csv("audit_data.csv")

X = df[["amount_lakh", "delay_days", "previous_issues"]]
y = df["severity"].map({"LOW": 0, "HIGH": 1})

xgb_model = XGBClassifier(
    n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42
)

xgb_model.fit(X, y)

isolation_model = IsolationForest(contamination=0.2, random_state=42)

isolation_model.fit(X)


class ContractorRequest(BaseModel):
    contractor_id: str
    amount_lakh: float
    delay_days: int
    previous_issues: int


@app.get("/")
def home():
    return {"message": "Government Audit Intelligence Platform is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/analyze")
def analyze_contractor(data: ContractorRequest):
    features = pd.DataFrame(
        [[data.amount_lakh, data.delay_days, data.previous_issues]],
        columns=["amount_lakh", "delay_days", "previous_issues"],
    )

    severity_prediction = xgb_model.predict(features)
    anomaly_prediction = isolation_model.predict(features)

    severity = "HIGH" if severity_prediction[0] == 1 else "LOW"
    anomaly = "YES" if anomaly_prediction[0] == -1 else "NO"

    if severity == "HIGH" and anomaly == "YES":
        risk = "CRITICAL"
        risk_score = 100
    elif severity == "HIGH" or anomaly == "YES":
        risk = "HIGH"
        risk_score = 70
    else:
        risk = "LOW"
        risk_score = 30

    return {
        "contractor_id": data.contractor_id,
        "amount_lakh": data.amount_lakh,
        "delay_days": data.delay_days,
        "previous_issues": data.previous_issues,
        "severity": severity,
        "anomaly": anomaly,
        "risk": risk,
        "risk_score": risk_score,
    }
