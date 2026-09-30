import pandas as pd
from html import escape

CONTRACTOR = "WAPCOS"   

clean = pd.read_csv("contractor_names_fallback.csv")   # one name per row
mapped = pd.read_csv("findings_mapped.csv")

counts = clean["contractor_name"].value_counts()
n_contractors = counts.size
n_repeat = int((counts > 1).sum())

rows = mapped[mapped["CONTRACTOR NAME"].astype(str)
              .str.contains(CONTRACTOR, case=False, na=False)]
names = rows["CONTRACTOR NAME"].astype(str).str.split(";").explode().str.strip()
full_name = names[names.str.contains(CONTRACTOR, case=False)].iloc[0]

def money(x):
    return "n/a" if pd.isna(x) else f"Rs {x:,.2f} crore"

def year(x):
    return "n/a" if pd.isna(x) else str(int(x))

items = ""
for _, r in rows.iterrows():
    ftype = "Not classified" if pd.isna(r["FINDING TYPE"]) else r["FINDING TYPE"]
    items += (
        "<li><b>{}</b> ({}, {})<br><small>{}</small></li>".format(
            escape(str(ftype)), money(r["AMOUNT (CRORES)"]),
            year(r["YEAR"]), escape(str(r["SOURCE CITATION"])))
    )

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Weekly Audit Tip Sheet</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; color: #222; }}
h1 {{ color: #1f3a5f; }}
li {{ margin-bottom: 12px; }}
small {{ color: #555; }}
</style></head><body>
<h1>Government Audit Intelligence Platform</h1>
<h2>Weekly Audit Tip Sheet</h2>
<p><b>Contractors with findings on record:</b> {n_contractors}<br>
<b>Contractors named in more than one finding:</b> {n_repeat}</p>
<h3>Featured Contractor</h3>
<p><b>{escape(full_name)}</b> has {len(rows)} findings on record:</p>
<ul>{items}</ul>
<p><small>Amounts are per audit paragraph; a paragraph may name more than one entity.</small></p>
<h3>Key Tip</h3>
<p>Start with contractors who appear in more than one audit paragraph, and check each finding against its source citation.</p>
<h3>Weekly Summary</h3>
<ul>
<li>Review contractors named in repeated findings.</li>
<li>Verify amounts and years against the cited report and page.</li>
<li>Fill in missing amounts and years for paragraphs still marked for manual review.</li>
</ul>
</body></html>"""

with open("weekly_tip_sheet_real.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Created weekly_tip_sheet_real.html")