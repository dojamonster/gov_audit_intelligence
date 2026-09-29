import json
import pandas as pd

df = pd.read_csv("findings_split.csv")
df = df[df["para_text"].notna()]


def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def make_record(row):
    names = clean(row["CONTRACTOR NAME"])
    names = [n.strip() for n in names.split(";") if n.strip()] if names else []
    amount = pd.to_numeric(row["AMOUNT (CRORES)"], errors="coerce")
    return {
        "input": row["para_text"],
        "output": {
            "finding_type": clean(row["FINDING TYPE"]),
            "amount_crore": None if pd.isna(amount) else float(amount),
            "department": clean(row["DEPARTMENT"]),
            "scheme": clean(row["SCHEME"]),
            "district": clean(row["district"]),
            "state": clean(row["STATE"]),
            "year": clean(row["YEAR"]),
            "contractor_names": names,
            "official_designation": clean(row["OFFICIAL DESIGNATION"]),
        },
    }


train_df = df[df["split"] == "train"]
val_df = train_df.sample(20, random_state=42)
train_df = train_df.drop(val_df.index)
test_df = df[df["split"] == "test"]

for name, part in [("train", train_df), ("val", val_df), ("test", test_df)]:
    with open(f"{name}.jsonl", "w", encoding="utf-8") as f:
        for _, row in part.iterrows():
            f.write(json.dumps(make_record(row), ensure_ascii=False) + "\n")
    print(name, len(part))
