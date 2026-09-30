import re
import pandas as pd
from rapidfuzz import fuzz

# ---------- 1. LOAD + SPLIT NAMES ----------
df = pd.read_csv("findings_clean_3.csv")

def split_names(cell):
    # split on ';' only when NOT inside brackets
    parts, depth, cur = [], 0, ""
    for ch in cell:
        if ch == "(": depth += 1
        if ch == ")": depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]

names = []
for cell in df["CONTRACTOR NAME"].dropna().astype(str):
    names += split_names(cell)

# ---------- 2. DROP JUNK ----------
junk = ["not named", "annexure", "none", "nan"]
names = [n for n in names if not any(j in n.lower() for j in junk)]

# ---------- 3. ADD HAND-MADE TEST VARIANTS ----------
# (real data has few true variants; label these as hand-made on your slide)
handmade = [
    "Shree Ram Constructions Pvt Ltd", "Shree Ram Construction Co.", "S R Constructions",
    "Ram Constructions UP", "Ram Constructions Bihar",
    "M/s Sharma Infra Projects Pvt. Ltd.", "Sharma Infrastructure Projects Private Limited",
    "Tata Consultancy Services Ltd", "M/s TCS",
    "Municipal Corporation of Greater Mumbai", "MCGM",
]
names += handmade

# ---------- 4. CLEAN ----------
def clean(n):
    n = n.lower()
    n = re.sub(r"\(.*?\)", " ", n)              # remove bracket notes
    n = re.sub(r"\bm/s\b", " ", n)
    n = re.sub(r"\b(pvt|private|ltd|limited|co|company|llp)\b", " ", n)
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    return re.sub(r"\s+", " ", n).strip()

raw = sorted(set(names))
cleaned = [clean(n) for n in raw]
print(f"{len(raw)} unique names\n")

# ---------- 5. RAPIDFUZZ (spelling similarity, 0-100) ----------
pairs = [(i, j) for i in range(len(raw)) for j in range(i + 1, len(raw))]
fz = {p: fuzz.token_sort_ratio(cleaned[p[0]], cleaned[p[1]]) for p in pairs}

# ---------- 6. LaBSE (meaning similarity, -1 to 1) ----------
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("sentence-transformers/LaBSE")
emb = model.encode(cleaned, normalize_embeddings=True)
sim = util.cos_sim(emb, emb)
lb = {p: sim[p[0]][p[1]].item() for p in pairs}

# ---------- 7. PRINT RESULTS ----------
def show(title, keys):
    print("=" * 80); print(title); print("=" * 80)
    for i, j in keys:
        print(f"fuzzy {fz[(i,j)]:5.1f} | LaBSE {lb[(i,j)]:.2f} | {raw[i]}  <->  {raw[j]}")
    print()

show("TOP 25 BY RAPIDFUZZ", sorted(pairs, key=fz.get, reverse=True)[:25])
show("TOP 25 BY LaBSE", sorted(pairs, key=lb.get, reverse=True)[:25])

# LaBSE likes it, rapidfuzz doesn't  -> your headline examples
labse_only = [p for p in pairs if lb[p] > 0.75 and fz[p] < 60]
show("LaBSE HIGH, FUZZY LOW", sorted(labse_only, key=lb.get, reverse=True)[:15])

# rapidfuzz likes it, LaBSE doesn't
fuzzy_only = [p for p in pairs if fz[p] > 75 and lb[p] < 0.6]
show("FUZZY HIGH, LaBSE LOW", sorted(fuzzy_only, key=fz.get, reverse=True)[:15])

# save everything so you can open it in Excel
pd.DataFrame([{"name_a": raw[i], "name_b": raw[j], "fuzzy": fz[(i,j)], "labse": round(lb[(i,j)],3)}
              for i, j in pairs]).sort_values("labse", ascending=False).to_csv("pair_scores.csv", index=False)
print("Saved pair_scores.csv")


import pandas as pd
pd.DataFrame({"contractor_name": raw, "cleaned_name": cleaned}).to_csv("contractor_names.csv", index=False)