import subprocess
import sys
import os
import logging
from datetime import datetime


def setup_launcher_logger():
    log_dir = os.path.join(os.getenv("LOCALAPPDATA", os.getcwd()), "PDFTools", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir, f"merge_launcher_{datetime.now().strftime('%Y-%m-%d')}.log"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )
    return log_file


def main():
    setup_launcher_logger()

    # Log everything Windows passed — this is the key diagnostic line
    logging.info(f"merge_launcher called. sys.argv = {sys.argv}")

    base_dir = os.path.dirname(sys.executable)
    app_path = os.path.join(base_dir, "merge_app.exe")

    # Pass all PDF arguments (Windows sends them all at once with MultiSelectModel=Player + %*)
    pdf_args = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")][:6]

    logging.info(f"Forwarding {len(pdf_args)} PDF(s) to merge_app.exe: {pdf_args}")
    logging.info(f"merge_app.exe path: {app_path}")

    subprocess.Popen([app_path] + pdf_args, close_fds=True)


if __name__ == "__main__":
    main()
