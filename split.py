import pandas as pd
df = pd.read_csv("findings_proto.csv")
df["split"] = "train"
df.loc[df.sample(40, random_state=42).index, "split"] = "test"
df.to_csv("findings_split.csv", index=False)
