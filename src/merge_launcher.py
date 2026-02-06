import sys
import os
import json
import logging
import subprocess
import msvcrt
from datetime import datetime

# ================= PATHS =================

BASE_DIR = os.path.join(
    os.getenv("LOCALAPPDATA", os.getcwd()),
    "PDFTools",
    "ipc"
)

QUEUE_FILE = os.path.join(BASE_DIR, "merge_queue.json")
LOCK_FILE = os.path.join(BASE_DIR, "merge_queue.lock")

LOG_DIR = os.path.join(
    os.getenv("LOCALAPPDATA", os.getcwd()),
    "PDFTools",
    "logs"
)

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ================= LOGGING =================

LOG_FILE = os.path.join(
    LOG_DIR,
    f"merge_launcher_{datetime.now().strftime('%Y-%m-%d')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [Launcher] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
)

# ================= FILE LOCK =================

def acquire_lock():
    lock_fp = open(LOCK_FILE, "a+")
    logging.info("Waiting for queue lock...")
    msvcrt.locking(lock_fp.fileno(), msvcrt.LK_LOCK, 1)
    logging.info("Queue lock acquired")
    return lock_fp

def release_lock(lock_fp):
    msvcrt.locking(lock_fp.fileno(), msvcrt.LK_UNLCK, 1)
    lock_fp.close()
    logging.info("Queue lock released")

# ================= QUEUE =================

def write_to_queue(pdf_path: str):
    lock_fp = acquire_lock()
    try:
        logging.info(f"Queueing PDF: {pdf_path}")

        queue_data = {"files": []}

        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    queue_data = json.load(f)
            except Exception as e:
                logging.error(f"Failed to read queue file: {e}")

        files = queue_data.get("files", [])
        if pdf_path not in files:
            files.append(pdf_path)

        queue_data["files"] = files
        queue_data["updated_at"] = datetime.now().isoformat()

        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue_data, f, indent=2)

        logging.info(f"Queue updated. Total PDFs: {len(files)}")

    finally:
        release_lock(lock_fp)

# ================= MAIN =================

def main():
    args = [
        arg for arg in sys.argv[1:]
        if arg.lower().endswith(".pdf")
    ]

    logging.info(f"Launcher started with args: {args}")

    for pdf in args:
        write_to_queue(pdf)

    # Launch merge_app ONLY ONCE
    marker = os.path.join(BASE_DIR, "merge_app_started.flag")

    lock_fp = acquire_lock()
    try:
        if os.path.exists(marker):
            logging.info("merge_app already launched — exiting")
            return

        with open(marker, "w"):
            pass

    finally:
        release_lock(lock_fp)

    logging.info("Launching merge_app.exe")

    base_dir = os.path.dirname(sys.executable)
    app_path = os.path.join(base_dir, "merge_app.exe")

    subprocess.Popen([app_path], close_fds=True)
    logging.info("merge_app.exe launched")

if __name__ == "__main__":
    main()
