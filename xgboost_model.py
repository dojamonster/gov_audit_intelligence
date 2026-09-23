import pandas as pd
from xgboost import XGBClassifier

df = pd.read_csv("audit_data.csv")

X = df[["amount_lakh", "delay_days", "previous_issues"]]

y = df["severity"].map({"LOW": 0, "HIGH": 1})

model = XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss",
)

model.fit(X, y)


def predict_severity(amount_lakh, delay_days, previous_issues):
    new_data = pd.DataFrame(
        {
            "amount_lakh": [amount_lakh],
            "delay_days": [delay_days],
            "previous_issues": [previous_issues],
        }
    )

    probability = model.predict_proba(new_data)[0][1]
    risk_score = round(probability * 100)

    if risk_score >= 70:
        severity = "HIGH"
    else:
        severity = "LOW"

    return severity, risk_score


severity, risk_score = predict_severity(500, 15, 3)

print("Model trained successfully!")
print("Predicted Severity:", severity)
print("Risk Score:", risk_score)
