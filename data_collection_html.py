import requests
BASE = "https://cag.gov.in"
LISTING_URL = f"{BASE}/en/audit-report"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CAGResearchBot/1.0; +research use)"
}

STATE_IDS = {
    "Bihar": "67",
    "Maharashtra": "79",
    "Uttar Pradesh": "90",
}


def fetch_filtered_html(state_ids: list[str], year_from: int = 2014, year_to: str = "") -> str:
    params = {
        "ts": "allwords",
        "title": "",
        "gt": "49",          
        "udt": "",
        "state": "",        
        "state[]": state_ids,
        "lbt": "",
        "sector": "",
        "sector[]": "",
        "report_type": "",
        "report_type[]": "",
        "od": "=",
        "yrf": str(year_from),
        "yrt": str(year_to),
    }

    resp = requests.get(LISTING_URL, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()

    print(f"Requested URL: {resp.url}")
    return resp.text


if __name__ == "__main__":
    selected_ids = [STATE_IDS["Bihar"], STATE_IDS["Maharashtra"]]

    html = fetch_filtered_html(selected_ids, year_from=2014)

    with open("retrieved_data_bihar_maharashtra.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved {len(html):,} characters to retrieved_data_bihar_maharashtra.html")