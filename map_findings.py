import pandas as pd

df = pd.read_csv("findings_proto.csv")
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

CATEGORIES = {
    "unfruitful_expenditure", "excess_payment", "non_utilisation",
    "diversion_of_funds", "procurement_violation", "quality_failure",
    "rush_of_expenditure", "outstanding_utilisation_certificates",
    "outstanding_suspense_remittance_balances",
}


EXTRA = {
    "Non-utilisation / untraceable funds": "non_utilisation",
    "non_utilisation_of_funds": "non_utilisation",
    "food_scheme_fund_non_utilisation": "non_utilisation",
    "unutilised_scheme_provision": "non_utilisation",
    "Misappropriation of Government money": "diversion_of_funds",
    "excess_expenditure_not_regularised": "excess_payment",
}

def to_category(x):
    if pd.isna(x):
        return "unknown"
    x = str(x).strip()
    if x in CATEGORIES:
        return x
    return EXTRA.get(x, "other")

df["category"] = df["FINDING TYPE"].map(to_category)
df.to_csv("findings_mapped.csv", index=False)

print(df["category"].value_counts().to_string())