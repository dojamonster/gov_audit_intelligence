import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("audit_data.csv")

X = df[["amount_lakh", "delay_days", "previous_issues"]]

model = IsolationForest(contamination=0.2, random_state=42)

df["anomaly"] = model.fit_predict(X)

print(df[["contractor_id", "amount_lakh", "delay_days", "previous_issues", "anomaly"]])

for _, row in df.iterrows():
    if row["anomaly"] == -1:
        print(f"{row['contractor_id']} -> ANOMALY")
    else:
        print(f"{row['contractor_id']} -> NORMAL")
