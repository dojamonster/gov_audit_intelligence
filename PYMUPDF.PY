import json
import os

import fitz

FOLDER = "downloaded_pdfs"
OUTPUT_FILE = "page_classification.json"

MIN_TEXT_CHARS = 50


def classify_pdf(filepath: str) -> dict:
   
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        return {"error": str(e)}

    pages = []
    scanned_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        char_count = len(text)

        classification = "text_native" if char_count >= MIN_TEXT_CHARS else "needs_ocr"
        if classification == "needs_ocr":
            scanned_count += 1

        pages.append({
            "page": page_num + 1,
            "char_count": char_count,
            "classification": classification,
        })

    doc.close()

    return {
        "total_pages": len(pages),
        "pages_needing_ocr": scanned_count,
        "pages": pages,
    }


def classify_all_pdfs(folder: str) -> dict:
    results = {}

    pdf_files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDF files to classify\n")

    for i, filename in enumerate(pdf_files, start=1):
        filepath = os.path.join(folder, filename)
        print(f"[{i}/{len(pdf_files)}] Classifying: {filename}")

        result = classify_pdf(filepath)

        if "error" in result:
            print(f"  FAILED to open: {result['error']}")
        else:
            print(f"  {result['total_pages']} pages, "
                  f"{result['pages_needing_ocr']} flagged for OCR")

        results[filename] = result

    return results


def save_results(results: dict, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved classification results to {filename}")


if __name__ == "__main__":
    results = classify_all_pdfs(FOLDER)
    save_results(results, OUTPUT_FILE)

    
    total_pages = sum(r.get("total_pages", 0) for r in results.values() if "error" not in r)
    total_ocr = sum(r.get("pages_needing_ocr", 0) for r in results.values() if "error" not in r)
    failed = sum(1 for r in results.values() if "error" in r)

    print(f"\n=== Summary ===")
    print(f"Total pages across all PDFs: {total_pages}")
    print(f"Pages flagged for OCR: {total_ocr}")
    print(f"Files that failed to open: {failed}")