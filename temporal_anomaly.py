import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("audit_data.csv")

df["audit_date"] = pd.to_datetime(df["audit_date"])

df["exposure_score"] = (
    df["amount_lakh"] +
    (df["delay_days"] * 5) +
    (df["previous_issues"] * 20)
)

features = df[[
    "amount_lakh",
    "delay_days",
    "previous_issues",
    "exposure_score"
]]

model = IsolationForest(
    contamination=0.2,
    random_state=42
)

df["anomaly"] = model.fit_predict(features)

df["anomaly_status"] = df["anomaly"].apply(
    lambda x: "ANOMALY" if x == -1 else "NORMAL"
)

df = df.sort_values("audit_date")

print(df[[
    "contractor_id",
    "audit_date",
    "exposure_score",
    "anomaly_status"
]])
df.to_csv("temporal_anomaly_results.csv", index=False)