import re
import pandas as pd

df = pd.read_csv("findings_proto.csv")
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

NAME = "CONTRACTOR NAME"
KEEP = ["Para_id", "FINDING TYPE", "AMOUNT (CRORES)", "YEAR",
        "SOURCE PAGE", "SOURCE CITATION"]

SKIP = [r"\bPWD\b", r"Public Works Department", r"\bUPDESCO\b",
        r"14 private firms", r"Annexure"]

print("rows with a contractor name:", df[NAME].notna().sum(), "of", len(df))

df[NAME] = df[NAME].fillna("").astype(str).str.split(";")
df = df.explode(NAME)
df[NAME] = df[NAME].str.strip()
df = df[df[NAME] != ""]

# remove the skip list
skip_mask = df[NAME].str.contains("|".join(SKIP), case=False, regex=True)
print("removed by skip list:")
print(df.loc[skip_mask, NAME].value_counts())
df = df[~skip_mask]


def key(n):
    n = re.sub(r"\(.*?\)", "", n)
    n = re.sub(r"^m/s\s+", "", n.strip(), flags=re.I)
    n = re.sub(r"[.,]", " ", n)
    n = re.sub(r"\b(ltd|limited|pvt|private)\b", "", n, flags=re.I)
    return re.sub(r"\s+", " ", n).strip().lower()


df["_key"] = df[NAME].map(key)
canon = df.groupby("_key")[NAME].agg(lambda s: min(s, key=len))
df[NAME] = df["_key"].map(canon)

out = df[[NAME] + KEEP].rename(columns={NAME: "contractor_name"})
out.to_csv("contractor_names_fallback.csv", index=False)

print()
print(len(out), "rows,", out["contractor_name"].nunique(), "unique contractors")
print("contractors appearing more than once:")
print(out["contractor_name"].value_counts().loc[lambda s: s > 1])