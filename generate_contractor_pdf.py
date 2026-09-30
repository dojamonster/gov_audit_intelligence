import pandas as pd
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle)

CONTRACTOR = "WAPCOS"   # change this one line to switch contractor
OUT = f"{CONTRACTOR}_risk_profile.pdf"

df = pd.read_csv("findings_mapped.csv")
rows = df[df["CONTRACTOR NAME"].astype(str)
          .str.contains(CONTRACTOR, case=False, na=False)].copy()
if rows.empty:
    raise SystemExit(f"No rows found for {CONTRACTOR}")

names = rows["CONTRACTOR NAME"].astype(str).str.split(";").explode().str.strip()
full_name = names[names.str.contains(CONTRACTOR, case=False)].iloc[0]

total = rows["AMOUNT (CRORES)"].sum()
n_cat = rows.loc[~rows["category"].isin(["other", "unknown"]), "category"].nunique()

styles = getSampleStyleSheet()
small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=7, leading=9)
head = ParagraphStyle("head", parent=small, textColor=colors.white,
                      fontName="Helvetica-Bold")

def cell(text, style=small):
    return Paragraph(escape(str(text)), style)

def money(x):
    return "n/a" if pd.isna(x) else f"{x:,.2f}"

def year(x):
    return "n/a" if pd.isna(x) else str(int(x))

data = [[cell(h, head) for h in
         ["Para", "Finding type", "Category", "Amount (Rs crore)", "Year", "Source citation"]]]
for _, r in rows.iterrows():
    ftype = "Not classified" if pd.isna(r["FINDING TYPE"]) else r["FINDING TYPE"]
    cat = "-" if r["category"] in ("unknown", "other") else r["category"]
    data.append([cell(r["Para_id"]), cell(ftype), cell(cat),
                 cell(money(r["AMOUNT (CRORES)"])), cell(year(r["YEAR"])),
                 cell(r["SOURCE CITATION"])])
table = Table(data, colWidths=[75, 85, 92, 45, 30, 196], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f9")]),
]))

story = [
    Paragraph("Government Audit Intelligence Platform", styles["Title"]),
    Spacer(1, 12),
    Paragraph("Contractor Risk Profile", styles["Heading2"]),
    Spacer(1, 8),
    Paragraph(f"<b>Contractor:</b> {escape(full_name)}", styles["BodyText"]),
    Paragraph(f"<b>Audit findings on record:</b> {len(rows)}", styles["BodyText"]),
    Paragraph(f"<b>Total amount across these paragraphs:</b> Rs {total:,.2f} crore "
              "(paragraph totals; a paragraph may name more than one entity)",
              styles["BodyText"]),
    Paragraph(f"<b>Distinct finding categories:</b> {n_cat}", styles["BodyText"]),
    Spacer(1, 14),
    Paragraph("Findings and sources", styles["Heading3"]),
    Spacer(1, 6),
    table,
]

SimpleDocTemplate(OUT, pagesize=A4, leftMargin=36, rightMargin=36,
                  topMargin=40, bottomMargin=40).build(story)
print("Created", OUT, "with", len(rows), "findings")