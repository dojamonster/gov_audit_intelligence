import pandas as pd

df = pd.read_csv("findings_proto.csv")
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

NAME = "CONTRACTOR NAME"
KEEP = ["Para_id", "FINDING TYPE", "AMOUNT (CRORES)", "YEAR",
        "SOURCE PAGE", "SOURCE CITATION"]

SKIP = [r"\bPWD\b", r"Public Works Department", r"\bUPDESCO\b", r"14 private firms"]

print("rows with a contractor name:", df[NAME].notna().sum(), "of", len(df))

# one name per row: split cells on ";"
df[NAME] = df[NAME].fillna("").astype(str).str.split(";")
df = df.explode(NAME)
df[NAME] = df[NAME].str.strip()
df = df[df[NAME] != ""]

# remove the skip list
skip_mask = df[NAME].str.contains("|".join(SKIP), case=False, regex=True)
print("removed by skip list:")
print(df.loc[skip_mask, NAME].value_counts())
df = df[~skip_mask]

out = df[[NAME] + KEEP].rename(columns={NAME: "contractor_name"})
out.to_csv("contractor_names_fallback.csv", index=False)

print()
print(len(out), "rows,", out["contractor_name"].nunique(), "unique contractors")
print("contractors appearing more than once:")
print(out["contractor_name"].value_counts().loc[lambda s: s > 1])