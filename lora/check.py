import pandas as pd
d = pd.read_csv("pair_scores.csv")
keys = ["wapcos", "mastek", "tcs", "tata consultancy", "mcgm", "greater mumbai", "sharma", "shree ram"]
mask = d.apply(lambda r: any(k in (r.name_a + r.name_b).lower() for k in keys), axis=1)
print(d[mask].to_string())