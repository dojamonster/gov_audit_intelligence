import json
import os
import subprocess

INPUT_FOLDER = "downloaded_pdfs"
OUTPUT_FOLDER = "ocred_pdfs"
CLASSIFICATION_FILE = "page_classification.json"


def load_classification(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ocr_page_ranges(pages: list[dict]) -> str:
    flagged_pages = []

    for page_info in pages:
        if page_info["classification"] == "needs_ocr":
            flagged_pages.append(str(page_info["page"]))

    return ",".join(flagged_pages)


def run_ocr(input_path: str, output_path: str, page_range: str) -> bool:
    
    command = [
        "ocrmypdf",
        "--pages", page_range,
        "--skip-text",
        input_path,
        output_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  OCR FAILED: {result.stderr.strip()[:300]}")
        return False

    return True


def process_all(classification: dict) -> None:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    files_with_ocr_needed = {
        fname: data for fname, data in classification.items()
        if "error" not in data and data.get("pages_needing_ocr", 0) > 0
    }

    print(f"{len(files_with_ocr_needed)} files have pages needing OCR\n")

    for i, (filename, data) in enumerate(files_with_ocr_needed.items(), start=1):
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        if os.path.exists(output_path):
            print(f"[{i}/{len(files_with_ocr_needed)}] Already OCR'd, skipping: {filename}")
            continue

        page_range = get_ocr_page_ranges(data["pages"])
        print(f"[{i}/{len(files_with_ocr_needed)}] OCR'ing {filename} "
              f"(pages: {page_range})...")

        success = run_ocr(input_path, output_path, page_range)
        if success:
            print(f"  Done: {output_path}")


if __name__ == "__main__":
    classification = load_classification(CLASSIFICATION_FILE)
    process_all(classification)