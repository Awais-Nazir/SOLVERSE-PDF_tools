import subprocess
import sys
import os
import logging
import ctypes
from ctypes import wintypes
from ipc_single_instance import send_files_to_existing_instance

MUTEX_NAME = "Global\\PDFToolsMerge_Mutex"

# ================= LOGGER =================
def setup_logger():
    log_dir = os.path.join(
        os.getenv("LOCALAPPDATA", os.getcwd()),
        "PDFTools",
        "logs"
    )
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "merge_launcher.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")]
    )
    return log_file

def log(msg):
    logging.info(f"[Launcher] {msg}")


def create_named_mutex(name):
    """
    Create or open a system-wide named mutex.
    Returns (handle, already_exists_flag)
    """
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    # CreateMutex signature
    CreateMutex = kernel32.CreateMutexW
    CreateMutex.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    CreateMutex.restype = wintypes.HANDLE

    handle = CreateMutex(None, False, name)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())

    # Determine if mutex already existed
    ERROR_ALREADY_EXISTS = 183
    already_exists = (ctypes.get_last_error() == ERROR_ALREADY_EXISTS)
    return handle, already_exists


def main():
    LOG_FILE = setup_logger()
    log(f"Launcher started with args: {sys.argv[1:]}")

    try:
        mutex_handle, existed = create_named_mutex(MUTEX_NAME)
    except Exception as e:
        log(f"Failed to create/open mutex: {e}")
        # Fallback: behave like no mutex (forward only)
        existed = True

    # If already exists → send args via IPC and exit
    if existed and len(sys.argv) > 1:
        log("Mutex already exists — this is a secondary instance")
        files = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")]
        if files:
            forwarded = send_files_to_existing_instance(files)
            log(f"Sent files via IPC: {files} (forwarded={forwarded})")
        else:
            log("No PDF arguments found to forward")
        return

    # Otherwise this is the primary
    log("This is primary instance — launching merge_app")

    base_dir = os.path.dirname(sys.executable)
    app_path = os.path.join(base_dir, "merge_app.exe")

    args = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")]

    log(f"Launching merge_app.exe with args: {args}")
    subprocess.Popen([app_path] + args, close_fds=True)
    log("merge_app.exe launched successfully")


if __name__ == "__main__":
    main()


# ask chatgpt to not include this ipc forwading in this merge_launcher.py file 
# as ipc forwarding is already handled in merge_app.py 