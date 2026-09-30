import altair as alt
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

BASE = Path(__file__).parent

st.set_page_config(page_title="Government Audit Intelligence",
                   page_icon="🏛️", layout="wide")


SKIP = r"\bPWD\b|Public Works|UPDESCO|14 private|Annexure"


SKIP = r"\bPWD\b|Public Works|UPDESCO|14 private|Annexure"


@st.cache_data
def load_data():
    c = pd.read_csv(BASE / "contractor_names.csv")
    c = c[~c["contractor_name"].str.contains(SKIP, case=False, regex=True)].copy()
    canon = c.groupby("cleaned_name")["contractor_name"].agg(lambda s: min(s, key=len))
    c["contractor_name"] = c["cleaned_name"].map(canon)
    m = pd.read_csv(BASE / "findings_mapped.csv")
    info = m.drop_duplicates("Para_id").set_index("Para_id")
    c["FINDING TYPE"] = c["para_id"].map(info["FINDING TYPE"])
    c["category"] = c["para_id"].map(info["category"]).fillna("unknown")
    c = c.rename(columns={"para_id": "Para_id", "amount_crore": "AMOUNT (CRORES)",
                          "year": "YEAR", "source_citation": "SOURCE CITATION"})
    c["AMOUNT (CRORES)"] = pd.to_numeric(c["AMOUNT (CRORES)"], errors="coerce")
    c["YEAR"] = pd.to_numeric(c["YEAR"], errors="coerce")
    return c, m
def money(x):
    return "not extracted yet" if pd.isna(x) else f"{x:,.2f}"


def year(x):
    return "n/a" if pd.isna(x) else str(int(x))


def prep(rows):
    return pd.DataFrame({
        "Para": rows["Para_id"],
        "Finding type": rows["FINDING TYPE"].fillna("Not classified"),
        "Category": rows["category"].replace({"unknown": "-", "other": "-"}),
        "Amount (Rs crore)": rows["AMOUNT (CRORES)"].map(money),
        "Year": rows["YEAR"].map(year),
        "Source citation": rows["SOURCE CITATION"].fillna(""),
    })


def build_pdf(name, table_df, total, n_cat):
    styles = getSampleStyleSheet()
    small = ParagraphStyle("small", parent=styles["BodyText"],
                           fontSize=7, leading=9)
    head = ParagraphStyle("head", parent=small, textColor=colors.white,
                          fontName="Helvetica-Bold")

    def cell(t, s=small):
        return Paragraph(escape(str(t)), s)

    data = [[cell(h, head) for h in table_df.columns]]
    for row in table_df.itertuples(index=False):
        data.append([cell(v) for v in row])
    table = Table(data, colWidths=[75, 85, 92, 45, 30, 196], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f2f5f9")]),
    ]))
    story = [
        Paragraph("Government Audit Intelligence Platform", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Contractor Risk Profile", styles["Heading2"]),
        Paragraph(f"<b>Contractor:</b> {escape(name)}", styles["BodyText"]),
        Paragraph(f"<b>Audit findings on record:</b> {len(table_df)}",
                  styles["BodyText"]),
        Paragraph(f"<b>Total across these paragraphs:</b> Rs {total:,.2f} crore "
                  "(paragraph totals; a paragraph may name more than one entity)",
                  styles["BodyText"]),
        Paragraph(f"<b>Distinct finding categories:</b> {n_cat}",
                  styles["BodyText"]),
        Spacer(1, 14),
        Paragraph("Findings and sources", styles["Heading3"]),
        Spacer(1, 6),
        table,
    ]
    buf = BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36,
                      topMargin=40, bottomMargin=40).build(story)
    return buf.getvalue()

def bar(series):
    df = series.rename_axis("label").reset_index(name="count")
    return (
        alt.Chart(df)
        .mark_bar(color="#1f3a5f")
        .encode(
            y=alt.Y("label:N", sort="-x", title=None),
            x=alt.X("count:Q", title=None, scale=alt.Scale(zero=True)),
        )
        .properties(height=28 * len(df) + 30)
    )
c, m = load_data()
counts = c["contractor_name"].value_counts()

st.title("🏛️ Government Audit Intelligence Platform")
st.caption("Contractor findings from CAG audit reports, with source citations")

tab1, tab2, tab3 = st.tabs(["Overview", "Contractor profile", "About"])


with tab1:
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Findings (paragraphs)", len(m))
    k2.metric("With a named contractor", len(c))
    k3.metric("Contractors", counts.size)
    k4.metric("Named in 2+ findings", int((counts > 1).sum()))
    k5.metric("Regions", m["STATE"].nunique())

    cats = m["category"].value_counts()
    other = int(cats.get("other", 0) + cats.get("unknown", 0))
    core = cats.drop(["other", "unknown"], errors="ignore")

    left, right = st.columns(2)
    with left:
        st.subheader("Findings by category")
        st.altair_chart(bar(core), use_container_width=True)
        st.caption(f"{other} more findings are other audit types "
                   "(revenue and IT audits) or not yet classified.")
    with right:
        st.subheader("Findings by region")
        st.altair_chart(bar(m["STATE"].value_counts().head(10)),
                        use_container_width=True)
        st.caption("Central = union-government reports.")

    st.subheader("Contractors named most often")
    st.altair_chart(bar(counts.head(10)), use_container_width=True)

with tab2:
    names = list(counts.index)
    pick = st.selectbox("Search or select a contractor", names,
                        format_func=lambda n: f"{n} ({counts[n]} findings)")
    rows = c[c["contractor_name"] == pick]
    table_df = prep(rows)
    total = rows["AMOUNT (CRORES)"].sum()
    n_cat = rows.loc[~rows["category"].isin(["other", "unknown"]),
                     "category"].nunique()

    a, b, d = st.columns(3)
    a.metric("Findings on record", len(rows))
    b.metric("Total (Rs crore)", f"{total:,.2f}")
    d.metric("Distinct categories", n_cat)
    st.caption("Amounts are per audit paragraph; a paragraph may name "
               "more than one entity.")

    st.dataframe(table_df, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download risk profile PDF",
                       data=build_pdf(pick, table_df, total, n_cat),
                       file_name=f"{pick[:30].strip()}_risk_profile.pdf",
                       mime="application/pdf")

with tab3:
    st.markdown("""
**Data:** findings labeled from CAG audit reports (195 paragraphs).
Each row keeps its report, paragraph and page so it can be verified.

**Limits**
- Some amounts and years are not extracted yet and show as blank.
- Contractor names are cleaned (multi-name cells split, spelling variants merged).
- This page shows findings and citations only. It does not give a risk rating,
  because the real data has no severity or delay fields.
    """)