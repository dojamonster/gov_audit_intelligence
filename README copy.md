# Pattern – Contractor Search (prototype)

Search box over 195 hand-verified paragraphs from Indian CAG audit reports.
Type a contractor or company name to see every paragraph it appears in, with
finding type, amount, state, year and page citation.

- Single static page: `index.html` (data embedded, no backend)
- Name grouping is text cleaning only (no trained entity-resolution model yet)
- Amounts are for the whole cited paragraph, not one party's liability

Status: prototype. Severity and anomaly models are not shown because they are
not yet trained on real data.
