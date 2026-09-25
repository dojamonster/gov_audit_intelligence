import subprocess
import sys
from datetime import datetime

SCRIPTS_IN_ORDER = [
    "data_collection_html.py",
    "parsing_bs4.py",
    "pdfdownloaded.py",
]

LOG_FILE = "pipeline_log.txt"


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_script(script_name: str) -> bool:
    log(f"Starting: {script_name}")
    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log(f"FAILED: {script_name}")
        log(f"  stderr: {result.stderr.strip()[:500]}")
        return False

    log(f"Finished: {script_name}")
    return True


if __name__ == "__main__":
    log("=== Pipeline run started ===")

    for script in SCRIPTS_IN_ORDER:
        success = run_script(script)
        if not success:
            log(f"=== Pipeline STOPPED early due to failure in {script} ===")
            sys.exit(1)

    log("=== Pipeline run completed successfully ===")