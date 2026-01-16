import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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


LOG_FILE = setup_logger("split_pdf")


# ================= APP =================

class PDFSplitterApp:
    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title(f"Split PDF v{VERSION}")
        self.root.geometry("420x240")
        self.root.resizable(False, False)

        self.pdf_path = initial_file

        self.create_ui()
        self.update_label()

    # ============== UI ==============

    def create_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="PDF File:").grid(row=0, column=0, sticky="w")
        self.pdf_label = tk.Label(frame, text="Not selected", width=30, anchor="w")
        self.pdf_label.grid(row=0, column=1)

        tk.Button(frame, text="Select PDF", command=self.select_pdf)\
            .grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Pages per split:").grid(row=2, column=0, sticky="w")
        self.pages_entry = tk.Entry(frame, width=10)
        self.pages_entry.grid(row=2, column=1, sticky="w")
        self.pages_entry.insert(0, "1")

        self.split_button = tk.Button(frame, text="Split PDF", width=15, command=self.start_split)
        self.split_button.grid(row=3, column=1, pady=10, sticky="w")

        self.status_label = ttk.Label(frame, text="Ready")
        self.status_label.grid(row=4, column=1, pady=5)

        self.progress = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=260,
            mode="determinate",
            maximum=100
        )
        self.progress.grid(row=5, column=1, pady=5)
        self.progress['value'] = 0

    # ============== HELPERS ==============

    def update_label(self):
        self.pdf_label.config(
            text=os.path.basename(self.pdf_path) if self.pdf_path else "Not selected"
        )

    def select_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.update_label()

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

    # ============== SPLIT LOGIC ==============

    def start_split(self):
        if not self.pdf_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return

        try:
            pages_per_split = int(self.pages_entry.get())
            if pages_per_split <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Pages per split must be a positive number.")
            return

        self.split_button.config(state="disabled")
        self.status_label.config(text="Splitting PDF...")
        self.progress['value'] = 5  # Start progress at 5%

        threading.Thread(
            target=self.split_worker,
            args=(pages_per_split,),
            daemon=True
        ).start()

    def split_worker(self, pages_per_split):
        try:
            # Lazy imports (heavy)
            from PyPDF2 import PdfReader, PdfWriter

            logging.info(
                f"Starting split for: {self.pdf_path} "
                f"({pages_per_split} pages per split)"
            )

            # ---- Stage 1: Reading PDF (10%) ----
            self.root.after(0, lambda: (
                self.status_label.config(text="Reading PDF..."),
                self.progress.config(value=10)
            ))

            reader = PdfReader(self.pdf_path)
            total_pages = len(reader.pages)

            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            folder = os.path.dirname(self.pdf_path)

            processed_pages = 0

            # ---- Stage 2: Splitting Pages (10% → 90%) ----
            for split_index, start in enumerate(range(0, total_pages, pages_per_split), start=1):
                writer = PdfWriter()

                for page_num in range(start, min(start + pages_per_split, total_pages)):
                    writer.add_page(reader.pages[page_num])
                    processed_pages += 1

                    progress = 10 + int((processed_pages / total_pages) * 80)
                    self.root.after(
                        0,
                        lambda p=progress: self.progress.config(value=p)
                    )

                output_name = f"{base_name}_split_{split_index}.pdf"
                raw_output_path = os.path.join(folder, output_name)
                output_path = self.get_unique_filename(raw_output_path)

                with open(output_path, "wb") as f:
                    writer.write(f)

            logging.info(f"Successfully split PDF into {split_index} files.")

            # ---- Stage 3: Finalizing (100%) ----
            self.root.after(0, lambda: self.split_success(split_index))

        except Exception:
            logging.exception("Split failed")
            self.root.after(0, self.split_failed)

        # ============== CALLBACKS ==============

    def split_success(self, count):
        self.progress['value'] = 100
        self.status_label.config(text="Split completed")
        messagebox.showinfo("Success", f"PDF split successfully into {count} files.")
        self.root.destroy()

    def split_failed(self):
        self.progress['value'] = 0
        self.status_label.config(text="Split failed")
        messagebox.showerror(
            "Error",
            f"Failed to split PDF.\n\nA log file has been created:\n{LOG_FILE}"
            )
        self.root.destroy()


# ================= MAIN =================

def main():
    initial_file = None
    for arg in sys.argv[1:]:
        if arg.lower().endswith(".pdf"):
            initial_file = arg
            break

    root = tk.Tk()

    def safe_exit(event=None):
        logging.info("Application closed by user")
        root.destroy()

    root.bind("<Escape>", safe_exit)
    root.protocol("WM_DELETE_WINDOW", safe_exit)

    PDFSplitterApp(root, initial_file)
    root.mainloop()


if __name__ == "__main__":
    main()
