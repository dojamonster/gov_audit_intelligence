import pandas as pd

df = pd.read_csv("findings_proto.csv")
needs_fix = pd.read_csv("7_still_needs_manual_amount_year.csv")["Para_id"].tolist()
df.loc[df["Para_id"].isin(needs_fix), ["AMOUNT (CRORES)", "YEAR"]] = None
df.to_csv("findings_proto.csv", index=False)
