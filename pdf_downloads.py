import json
import os
import time

import requests

BASE = "https://cag.gov.in"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CAGResearchBot/1.0; +research use)"
}
DOWNLOAD_DELAY_SECONDS = 1.5
OUTPUT_FOLDER = "downloaded_pdfs"


def load_reports(filename: str) -> list[dict]:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def build_full_pdf_url(pdf_url: str) -> str:
    """pdf_url from the JSON starts with '/webroot/...' -- needs the domain prepended."""
    if pdf_url.startswith("http"):
        return pdf_url  
    return BASE + pdf_url


def safe_filename(title: str, report_id: str) -> str:
    """
    Build a filesystem-safe filename from the report title, since titles
    contain characters (commas, colons, slashes) that aren't safe in
    filenames on some systems. Keeping the report_id avoids collisions
    when two titles are very similar.
    """
    cleaned = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
    cleaned = cleaned.strip()[:100]  
    return f"{report_id}_{cleaned}.pdf"


def download_pdf(pdf_url: str, save_path: str) -> bool:
    
    try:
        resp = requests.get(pdf_url, headers=HEADERS, timeout=60, stream=True)
        resp.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return True

    except requests.exceptions.RequestException as e:
        print(f"  FAILED: {e}")
        return False


def download_all(reports: list[dict]) -> None:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    succeeded = 0
    failed = 0

    for i, report in enumerate(reports, start=1):
        pdf_url_raw = report.get("pdf_url")
        if not pdf_url_raw:
            print(f"[{i}/{len(reports)}] Skipping -- no pdf_url for: {report.get('title')}")
            continue

        full_url = build_full_pdf_url(pdf_url_raw)
        report_id = report.get("detail_url", "").rstrip("/").split("/")[-1] or str(i)
        filename = safe_filename(report.get("title", "untitled"), report_id)
        save_path = os.path.join(OUTPUT_FOLDER, filename)

        if os.path.exists(save_path):
            print(f"[{i}/{len(reports)}] Already downloaded, skipping: {filename}")
            continue

        print(f"[{i}/{len(reports)}] Downloading: {report.get('title')[:80]}...")

        if download_pdf(full_url, save_path):
            succeeded += 1
            print(f"  Saved as: {filename}")
        else:
            failed += 1

        time.sleep(DOWNLOAD_DELAY_SECONDS)  

    print(f"\nDone. {succeeded} downloaded, {failed} failed, out of {len(reports)} total.")


if __name__ == "__main__":
    reports = load_reports("cag_reports.json")
    print(f"Loaded {len(reports)} reports to download")

    download_all(reports)