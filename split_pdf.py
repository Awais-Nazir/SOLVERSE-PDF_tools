import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter


class PDFSplitterApp:
    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title("Split PDF with Python")
        self.root.geometry("400x180")
        self.root.resizable(False, False)

        self.pdf_path = initial_file

        self.create_ui()
        self.update_label()

        # ESC to close
        self.root.bind("<Escape>", lambda e: self.root.destroy())

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

        tk.Button(frame, text="Split PDF", command=self.split_pdf, width=15)\
            .grid(row=3, column=1, pady=15, sticky="w")

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


    def split_pdf(self):
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

        try:
            reader = PdfReader(self.pdf_path)
            total_pages = len(reader.pages)

            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            folder = os.path.dirname(self.pdf_path)

            split_count = 1
            for start in range(0, total_pages, pages_per_split):
                writer = PdfWriter()
                for page_num in range(start, min(start + pages_per_split, total_pages)):
                    writer.add_page(reader.pages[page_num])

                output_name = f"{base_name}_split_{split_count}.pdf"
                raw_output_path = os.path.join(folder, output_name)
                output_path = self.get_unique_filename(raw_output_path)

                with open(output_path, "wb") as f:
                    writer.write(f)


                split_count += 1

            messagebox.showinfo(
                "Success",
                f"PDF split successfully into {split_count - 1} files."
            )
            self.root.destroy()  # auto-close after success

        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF:\n{e}")


def main():
    initial_file = None
    for arg in sys.argv[1:]:
        if arg.lower().endswith(".pdf"):
            initial_file = arg
            break

    root = tk.Tk()
    app = PDFSplitterApp(root, initial_file)
    root.mainloop()


if __name__ == "__main__":
    main()
