import sys
import os
import json
import threading
import logging
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from version import VERSION

# ================= QUEUE =================

QUEUE_DIR = os.path.join(
    os.getenv("LOCALAPPDATA", os.getcwd()),
    "PDFTools",
    "ipc"
)

QUEUE_FILE = os.path.join(QUEUE_DIR, "merge_queue.json")
QUEUE_LOCK_FILE = os.path.join(QUEUE_DIR, "merge_queue.lock")
MERGE_APP_FLAG = os.path.join(QUEUE_DIR, "merge_app_started.flag")


def read_queue_files():
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("files", [])
    except Exception:
        logging.exception("Failed to read queue file")
        return []


def clear_queue():
    # logging.info("Clearing merge queue demo-version")
    # pass
    # from merge_launcher import release_lock
    try:
        if os.path.exists(QUEUE_FILE):
            os.remove(QUEUE_FILE)
            os.remove(MERGE_APP_FLAG)
            os.remove(QUEUE_LOCK_FILE)
            logging.info("Merge queue cleared")
    except Exception:
        logging.exception("Failed to clear queue")


# ================= LOGGER =================

def setup_logger(app_name):
    log_dir = os.path.join(
        os.getenv("LOCALAPPDATA", os.getcwd()),
        "PDFTools",
        "logs"
    )
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir,
        f"{app_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")]
    )

    logging.info(f"Application version: {VERSION}")
    return log_file


LOG_FILE = setup_logger("merge_app")

# ================= GUI =================

class PDFMergerApp:
    def __init__(self, root, initial_files=None):
        self.root = root
        self.root.title(f"Merge PDFs v{VERSION}")
        self.root.geometry("520x420")
        self.root.resizable(False, False)

        self.pdfs = list(initial_files or [])

        self.create_ui()
        self.refresh_listbox()

    # ---------- UI ----------

    def create_ui(self):
        frame = tk.Frame(self.root, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="PDF Files (merge order):").pack(anchor="w")

        self.listbox = tk.Listbox(frame, width=60, height=10)
        self.listbox.pack(pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add PDFs", command=self.add_pdfs).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove", command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Move Up", command=lambda: self.move(-1)).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Move Down", command=lambda: self.move(1)).grid(row=0, column=3, padx=5)

        self.merge_btn = tk.Button(frame, text="Merge PDFs", width=25, command=self.start_merge)
        self.merge_btn.pack(pady=10)

        self.status = ttk.Label(frame, text="Ready")
        self.status.pack()

        self.progress = ttk.Progressbar(frame, length=350, mode="determinate")
        self.progress.pack(pady=5)

    # ---------- List Handling ----------

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for f in self.pdfs:
            self.listbox.insert(tk.END, os.path.basename(f))

    def add_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            if f not in self.pdfs:
                self.pdfs.append(f)
        self.refresh_listbox()

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            del self.pdfs[i]
        self.refresh_listbox()

    def move(self, direction):
        sel = self.listbox.curselection()
        if not sel:
            return
        i = sel[0]
        j = i + direction
        if 0 <= j < len(self.pdfs):
            self.pdfs[i], self.pdfs[j] = self.pdfs[j], self.pdfs[i]
            self.refresh_listbox()
            self.listbox.select_set(j)

    # ---------- Merge ----------

    def start_merge(self):
        if len(self.pdfs) < 2:
            messagebox.showerror("Error", "Select at least two PDFs.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="merged.pdf"
        )

        if not save_path:
            return

        self.merge_btn.config(state="disabled")
        self.progress.start(10)
        self.status.config(text="Merging...")

        threading.Thread(
            target=self.merge_worker,
            args=(save_path,),
            daemon=True
        ).start()

    def merge_worker(self, output):
        try:
            from PyPDF2 import PdfMerger
            merger = PdfMerger()

            for i, pdf in enumerate(self.pdfs):
                merger.append(pdf)
                pct = int((i + 1) / len(self.pdfs) * 90)
                self.root.after(0, lambda v=pct: self.progress.config(value=v))

            merger.write(output)
            merger.close()

            self.root.after(0, self.merge_success)

        except Exception:
            logging.exception("Merge failed")
            self.root.after(0, self.merge_failed)

    def merge_success(self):
        self.progress.stop()
        self.progress.config(value=100)
        messagebox.showinfo("Success", "PDFs merged successfully!")
        self.root.destroy()

    def merge_failed(self):
        messagebox.showerror("Error", f"Merge failed.\n\nLog:\n{LOG_FILE}")
        self.root.destroy()


# ================= MAIN =================

def main():
    cli_files = [a for a in sys.argv[1:] if a.lower().endswith(".pdf")]
    queue_files = read_queue_files()

    initial_files = list(dict.fromkeys(queue_files + cli_files))
    clear_queue()

    root = tk.Tk()
    PDFMergerApp(root, initial_files)
    root.mainloop()


if __name__ == "__main__":
    main()
