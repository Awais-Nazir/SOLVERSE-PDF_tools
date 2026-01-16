import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfMerger
import logging
from datetime import datetime
from version import VERSION

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
    logging.info("========== Application Started ==========")
    logging.info(f"Executable Path: {sys.executable}")
    return log_file


LOG_FILE = setup_logger("merge_pdfs")

# ================= APP =================

class PDFMergerApp:
    def __init__(self, root, initial_files=None):
        self.root = root
        self.root.title(f"Merge PDFs v{VERSION}")
        self.root.geometry("520x340")
        self.root.resizable(False, False)

        self.pdf1 = None
        self.pdf2 = None

        if initial_files:
            if len(initial_files) >= 1:
                self.pdf1 = initial_files[0]
            if len(initial_files) >= 2:
                self.pdf2 = initial_files[1]

        self.create_ui()
        self.update_labels()

        # Auto-merge if launched from context menu with 2 PDFs
        if self.pdf1 and self.pdf2:
            self.root.after(300, self.start_merge)

    # ============== UI ==============

    def create_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="First PDF:").grid(row=0, column=0, sticky="w")
        self.label_pdf1 = tk.Label(frame, text="Not selected", width=40, anchor="w")
        self.label_pdf1.grid(row=0, column=1)

        tk.Button(frame, text="Select First PDF", command=self.select_pdf1)\
            .grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Second PDF:").grid(row=2, column=0, sticky="w")
        self.label_pdf2 = tk.Label(frame, text="Not selected", width=40, anchor="w")
        self.label_pdf2.grid(row=2, column=1)

        tk.Button(frame, text="Select Second PDF", command=self.select_pdf2)\
            .grid(row=3, column=1, sticky="w", pady=5)

        tk.Button(frame, text="Swap Order", command=self.swap_pdfs)\
            .grid(row=4, column=1, sticky="w", pady=10)

        self.merge_button = tk.Button(frame, text="Merge PDFs", width=20, command=self.start_merge)
        self.merge_button.grid(row=5, column=1, pady=10)

        self.status_label = ttk.Label(frame, text="Ready")
        self.status_label.grid(row=6, column=1, pady=5)

        self.progress = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=300,
            mode="indeterminate"
        )
        self.progress.grid(row=7, column=1, pady=5)

    # ============== HELPERS ==============

    def update_labels(self):
        self.label_pdf1.config(text=os.path.basename(self.pdf1) if self.pdf1 else "Not selected")
        self.label_pdf2.config(text=os.path.basename(self.pdf2) if self.pdf2 else "Not selected")

    def select_pdf1(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf1 = path
            self.update_labels()

    def select_pdf2(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf2 = path
            self.update_labels()

    def swap_pdfs(self):
        self.pdf1, self.pdf2 = self.pdf2, self.pdf1
        self.update_labels()

    def get_unique_filename(self, path):
        if not os.path.exists(path):
            return path
        base, ext = os.path.splitext(path)
        counter = 1
        while True:
            new_path = f"{base}[{counter}]{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    # ============== MERGE LOGIC ==============

    def start_merge(self):
        if not self.pdf1 or not self.pdf2:
            messagebox.showerror("Error", "Please select both PDFs.")
            return

        base_name = f"merged_{os.path.splitext(os.path.basename(self.pdf1))[0]}.pdf"
        default_dir = os.path.dirname(self.pdf1)

        save_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=base_name,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not save_path:
            return

        output_path = self.get_unique_filename(save_path)

        self.merge_button.config(state="disabled")
        self.status_label.config(text="Merging PDFs...")
        self.progress.start(10)

        threading.Thread(
            target=self.merge_worker,
            args=(output_path,),
            daemon=True
        ).start()

    def merge_worker(self, output_path):
        try:
            logging.info(f"Merging:\n1: {self.pdf1}\n2: {self.pdf2}\nOutput: {output_path}")

            merger = PdfMerger()
            merger.append(self.pdf1)
            merger.append(self.pdf2)
            merger.write(output_path)
            merger.close()

            logging.info("Merge completed successfully.")
            self.root.after(0, self.merge_success)

        except Exception:
            logging.exception("Merge failed")
            self.root.after(0, self.merge_failed)

    # ============== CALLBACKS ==============

    def merge_success(self):
        self.progress.stop()
        self.status_label.config(text="Merge completed")
        messagebox.showinfo("Success", "PDFs merged successfully!")
        self.root.destroy()

    def merge_failed(self):
        self.progress.stop()
        self.status_label.config(text="Merge failed")
        messagebox.showerror(
            "Error",
            f"Failed to merge PDFs.\n\nA log file has been created:\n{LOG_FILE}"
        )
        self.root.destroy()


# ================= MAIN =================

def main():
    initial_files = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")][:2]
    if len(initial_files) == 2:
        logging.info("Auto mode detected (context menu)")

    root = tk.Tk()

    def safe_exit(event=None):
        logging.info("Application closed by user")
        root.destroy()

    root.bind("<Escape>", safe_exit)
    root.protocol("WM_DELETE_WINDOW", safe_exit)

    PDFMergerApp(root, initial_files)
    root.mainloop()


if __name__ == "__main__":
    main()
