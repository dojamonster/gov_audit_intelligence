import json
import re

from bs4 import BeautifulSoup

BASE_URL = "https://cag.gov.in"


def load_html(filename: str) -> BeautifulSoup:
    with open(filename, "r", encoding="utf-8") as f:
        html = f.read()
    return BeautifulSoup(html, "html.parser")


def parse_report_listing(soup: BeautifulSoup) -> list[dict]:

    reports = []

    detail_links = soup.select('a[href*="/en/audit-report/details/"]')

    for link in detail_links:
        title = link.get_text(strip=True)
        if not title:
            continue

        detail_url = link["href"]
        if detail_url.startswith("/"):
            detail_url = BASE_URL + detail_url

            container = link.find_parent("div", class_="AuditReportlisting")
        if container is None:
            container = link.find_parent(["div", "article", "li"]) or link.parent

        pdf_link_tag = container.find("a", href=re.compile(r"download_audit_report"))
        pdf_url = pdf_link_tag["href"] if pdf_link_tag else None

        state_tag = container.select_one(".reportIcon h5")
        state = state_tag.get_text(strip=True) if state_tag else None

        date_tag = container.select_one(".dateFirst .dtn")
        date = date_tag.get_text(strip=True) if date_tag else None

        type_tags = container.select(".reportType span")
        report_types = [t.get_text(strip=True) for t in type_tags]

        reports.append({
            "title": title,
            "detail_url": detail_url,
            "pdf_url": pdf_url,
            "state": state,
            "date": date,
            "report_types": report_types
        })

    return reports


def save_to_json(reports: list[dict], filename: str = "cag_reports.json") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(reports)} report entries to {filename}")


if __name__ == "__main__":
    soup = load_html("retrieved_data_bihar_maharashtra.html")

    reports = parse_report_listing(soup)
    print(f"Parsed {len(reports)} reports")

    save_to_json(reports)