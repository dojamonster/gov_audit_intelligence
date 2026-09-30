import pandas as pd
d = pd.read_csv("pair_scores.csv")
d["labse_rank"]  = d["labse"].rank(ascending=False).astype(int)
d["fuzzy_rank"]  = d["fuzzy"].rank(ascending=False).astype(int)
total = len(d)

same = [   # true matches
 ("M/s TCS", "Tata Consultancy Services Ltd"),
 ("MCGM", "Municipal Corporation of Greater Mumbai"),
 ("M/s Sharma Infra Projects Pvt. Ltd.", "Sharma Infrastructure Projects Private Limited"),
 ("Shree Ram Constructions Pvt Ltd", "Shree Ram Construction Co."),
 ("Shree Ram Constructions Pvt Ltd", "S R Constructions"),
 ("M/s WAPCOS Limited", "WAPCOS Ltd"),
 ("M/s Mastek Ltd", "M/s Mastek Ltd (software developer, 2001)"),
]
diff = [   # different organisations
 ("Ram Constructions UP", "Ram Constructions Bihar"),
 ("Konkan IDC", "Tapi IDC"),
 ("Central Railway", "Western Railway"),
]

def show(title, pairs):
    print("\n" + title + f"  (rank out of {total}, 1 = most similar)")
    for a, b in pairs:
        r = d[((d.name_a == a) & (d.name_b == b)) | ((d.name_a == b) & (d.name_b == a))]
        if r.empty:
            print("  NOT FOUND:", a, "<->", b); continue
        r = r.iloc[0]
        print(f"  fuzzy {r.fuzzy:5.1f} (rank {r.fuzzy_rank:4d}) | LaBSE {r.labse:.2f} (rank {r.labse_rank:4d}) | {a} <-> {b}")

show("SAME ORGANISATION (want high scores, low rank numbers)", same)
show("DIFFERENT ORGANISATIONS (want low scores, high rank numbers)", diff)