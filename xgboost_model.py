import pandas as pd
from xgboost import XGBClassifier

df = pd.read_csv("audit_data.csv")

print("Audit Data:")
print(df)

X = df[["amount_lakh", "delay_days", "previous_issues"]]

y = df["severity"].map({"LOW": 0, "HIGH": 1})

model = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)

model.fit(X, y)

print("\nModel trained successfully!")

new_contractor = [[500, 15, 3]]

prediction = model.predict(new_contractor)

if prediction[0] == 1:
    print("Predicted Severity: HIGH")
else:
    print("Predicted Severity: LOW")
