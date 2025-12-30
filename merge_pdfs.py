import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger


class PDFMergerApp:
    def __init__(self, root, initial_files=None):
        self.root = root
        self.root.title("Merge PDFs with Python")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.pdf1 = None
        self.pdf2 = None
        # self.output_path = None

        if initial_files:
            if len(initial_files) >= 1:
                self.pdf1 = initial_files[0]
            if len(initial_files) >= 2:
                self.pdf2 = initial_files[1]

        self.create_ui()
        self.update_labels()

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        # Auto-merge if two PDFs are passed from context menu
        if self.pdf1 and self.pdf2:
            self.root.after(300, self.merge_pdfs)


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

        # tk.Button(frame, text="Choose Save Location", command=self.choose_output)\
        #     .grid(row=6, column=1, sticky="w", pady=5)

        tk.Button(frame, text="Merge PDFs", command=self.merge_pdfs, width=20)\
            .grid(row=7, column=1, pady=15)

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

    def merge_pdfs(self):
        if not self.pdf1 or not self.pdf2:
            messagebox.showerror("Error", "Please select both PDFs.")
            return

        base_name = f"merged_{os.path.splitext(os.path.basename(self.pdf1))[0]}.pdf"
        default_dir = os.path.dirname(self.pdf1)

        path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=base_name,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not path:
            return  # user cancelled save dialog

        output_path = self.get_unique_filename(path)

        try:
            merger = PdfMerger()
            merger.append(self.pdf1)
            merger.append(self.pdf2)

            with open(output_path, "wb") as f:
                merger.write(f)

            merger.close()

            messagebox.showinfo("Success", "PDFs merged successfully!")
            self.root.destroy()  # ✅ close app after success

        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{e}")


def main():
    initial_files = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")]
    initial_files = initial_files[:2]

    root = tk.Tk()
    app = PDFMergerApp(root, initial_files)
    root.mainloop()


if __name__ == "__main__":
    main()
