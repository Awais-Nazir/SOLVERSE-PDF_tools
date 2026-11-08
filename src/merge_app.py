import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from datetime import datetime
from version import VERSION
from merge_selection import MAX_PDFS
from windows_dpi import create_root_window

# ================= CONSTANTS =================

MIN_PDFS = 2

# ================= LOGGER =================


def setup_logger(app_name):
    log_dir = os.path.join(os.getenv("LOCALAPPDATA", os.getcwd()), "PDFTools", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"{app_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )

    logging.info(f"Application version: {VERSION}")
    logging.info("========== Application Started ==========")
    logging.info(f"Executable Path: {sys.executable}")
    return log_file


LOG_FILE = setup_logger("merge_app")

# ================= APP =================


class PDFMergerApp:
    def __init__(self, root, initial_files=None):
        self.root = root
        self.root.resizable(False, False)

        # Ordered list of PDF paths; None = empty slot
        self.pdfs = []

        if initial_files:
            self.pdfs = list(initial_files[:MAX_PDFS])
            logging.info(f"Launched with {len(self.pdfs)} PDF(s): {self.pdfs}")
        else:
            self.pdfs = [None, None]
            logging.info("Launched manually — showing 2 empty slots.")

        while len(self.pdfs) < MIN_PDFS:
            self.pdfs.append(None)

        # Drag state — tracked per-gesture to distinguish click vs drag
        self._drag_index = None
        self._drag_start_y = None
        self._did_drag = False  # True once cursor moves >5px

        self._build_window()
        self._build_ui()

    # ============== WINDOW ==============

    def _build_window(self):
        self.root.title(f"Merge PDFs v{VERSION}")
        self._update_geometry()

    def _update_geometry(self):
        height = 165 + len(self.pdfs) * 52
        self.root.geometry(f"560x{height}")

    # ============== UI ==============

    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, padx=16, pady=14)
        self.main_frame.pack(fill="both", expand=True)

        # Title row
        title_frame = tk.Frame(self.main_frame)
        title_frame.pack(fill="x", pady=(0, 8))
        tk.Label(
            title_frame,
            text="Merge PDFs",
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")
        tk.Label(
            title_frame,
            text="drag rows to reorder",
            font=("Segoe UI", 8),
            fg="#888888",
        ).pack(side="right", pady=(4, 0))

        # Slots container
        self.slots_frame = tk.Frame(self.main_frame)
        self.slots_frame.pack(fill="x")
        self.slot_widgets = []
        self._render_slots()

        # Bottom controls
        bottom = tk.Frame(self.main_frame)
        bottom.pack(fill="x", pady=(10, 0))

        self.btn_add = tk.Button(
            bottom, text="+ Add PDF", width=10, command=self.add_slot
        )
        self.btn_add.pack(side="left")

        self.btn_remove = tk.Button(
            bottom, text="- Remove Last", width=13, command=self.remove_last_slot
        )
        self.btn_remove.pack(side="left", padx=(6, 0))

        self.merge_button = tk.Button(
            bottom, text="Merge PDFs", width=14, command=self.start_merge
        )
        self.merge_button.pack(side="right")

        # Status + progress
        self.status_label = ttk.Label(self.main_frame, text="Ready")
        self.status_label.pack(anchor="w", pady=(8, 0))

        self.progress = ttk.Progressbar(
            self.main_frame, orient="horizontal", mode="determinate", maximum=100
        )
        self.progress.pack(fill="x", pady=(4, 0))

        self._refresh_buttons()

    # ============== SLOTS ==============

    def _render_slots(self):
        """Destroy and recreate all slot rows from self.pdfs."""
        for w in self.slot_widgets:
            w["frame"].destroy()
        self.slot_widgets = []
        for i, path in enumerate(self.pdfs):
            self._render_one_slot(i, path)

    def _render_one_slot(self, index, path):
        """
        Build one slot row. Drag and click-to-browse are separated cleanly:
        - ButtonPress   → record drag start position + index
        - B1-Motion     → if moved >5px, set _did_drag=True and show highlight
        - ButtonRelease → if NOT dragged, open file browser; if dragged, reorder
        All three events go through the same handler trio, bound on the row frame
        only — children propagate up naturally via Tkinter event bubbling.
        The clear (×) button uses its own command and stops propagation.
        """
        row = tk.Frame(
            self.slots_frame,
            relief="groove",
            bd=1,
            pady=4,
            padx=6,
        )
        row.pack(fill="x", pady=3)

        # Number badge
        badge = tk.Label(
            row,
            text=str(index + 1),
            width=2,
            font=("Segoe UI", 9, "bold"),
            fg="#555555",
            cursor="fleur",
        )
        badge.pack(side="left")

        # Drag handle (visual cue)
        handle = tk.Label(
            row,
            text=":::",
            fg="#bbbbbb",
            font=("Segoe UI", 10),
            cursor="fleur",
        )
        handle.pack(side="left", padx=(2, 6))

        # Filename / placeholder label
        if path:
            display = os.path.basename(path)
            fg = "#111111"
            cursor = "hand2"
        else:
            display = "Click anywhere here to select a PDF..."
            fg = "#aaaaaa"
            cursor = "hand2"

        file_label = tk.Label(
            row,
            text=display,
            anchor="w",
            fg=fg,
            font=("Segoe UI", 9),
            cursor=cursor,
        )
        file_label.pack(side="left", fill="x", expand=True)

        # Clear (×) button — only when a file is loaded
        if path:

            def _clear(i=index):
                self.pdfs[i] = None
                logging.info(f"Slot {i + 1} cleared.")
                self._refresh_slots()

            clear_btn = tk.Button(
                row,
                text="×",
                width=2,
                fg="#cc0000",
                relief="flat",
                cursor="arrow",
                command=_clear,
            )
            clear_btn.pack(side="right", padx=(4, 0))
            # Stop drag/click events from bubbling up from the clear button
            clear_btn.bind("<ButtonPress-1>", lambda e: "break")
            clear_btn.bind("<B1-Motion>", lambda e: "break")
            clear_btn.bind("<ButtonRelease-1>", lambda e: "break")

        # ── Bind drag+click trio on every widget EXCEPT the clear button ──
        # Tkinter does NOT bubble events up the widget tree automatically for
        # custom bindings — we must bind each child widget individually.
        drag_widgets = [row, badge, handle, file_label]

        for w in drag_widgets:
            w.bind("<ButtonPress-1>", lambda e, i=index: self._on_press(e, i))
            w.bind("<B1-Motion>", lambda e: self._on_motion(e))
            w.bind("<ButtonRelease-1>", lambda e, i=index: self._on_release(e, i))

        self.slot_widgets.append({"frame": row, "label": file_label})

    # ── Unified press / motion / release handlers ──────────────────────────

    def _on_press(self, event, index):
        """Record which slot the gesture started on."""
        self._drag_index = index
        self._drag_start_y = event.y_root
        self._did_drag = False

    def _on_motion(self, event):
        """Once cursor moves >5px vertically, switch into drag mode."""
        if self._drag_index is None or self._drag_start_y is None:
            return
        if abs(event.y_root - self._drag_start_y) < 5:
            return

        self._did_drag = True
        target = self._get_drag_target(event.y_root)
        default_bg = self.root.cget("bg")
        for i, w in enumerate(self.slot_widgets):
            highlight = i == target and i != self._drag_index
            w["frame"].config(bg="#ddeeff" if highlight else default_bg)

    def _on_release(self, event, index):
        """
        On release:
        - If no drag occurred → open file browser for this slot.
        - If drag occurred    → reorder self.pdfs and re-render.
        """
        if self._drag_index is None:
            return

        # Reset row backgrounds
        default_bg = self.root.cget("bg")
        for w in self.slot_widgets:
            w["frame"].config(bg=default_bg)

        if self._did_drag:
            # ── Drag: reorder ──
            target = self._get_drag_target(event.y_root)
            if target != self._drag_index:
                item = self.pdfs.pop(self._drag_index)
                self.pdfs.insert(target, item)
                logging.info(
                    f"Reordered: position {self._drag_index + 1} → {target + 1}"
                )
                self._render_slots()
        else:
            # ── Click: open file browser ──
            self._browse_slot(index)

        # Reset drag state
        self._drag_index = None
        self._drag_start_y = None
        self._did_drag = False

    # ──────────────────────────────────────────────────────────────────────

    def _get_drag_target(self, y_root):
        for i, w in enumerate(self.slot_widgets):
            f = w["frame"]
            top = f.winfo_rooty()
            bot = top + f.winfo_height()
            if top <= y_root < bot:
                return i
        if self.slot_widgets:
            last = self.slot_widgets[-1]["frame"]
            if y_root >= last.winfo_rooty() + last.winfo_height():
                return len(self.pdfs) - 1
        return 0

    def _browse_slot(self, index):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdfs[index] = path
            logging.info(f"Slot {index + 1} set via browser: {path}")
            self._refresh_slots()

    # ============== ADD / REMOVE SLOTS ==============

    def add_slot(self):
        if len(self.pdfs) >= MAX_PDFS:
            messagebox.showinfo("Limit reached", f"Maximum {MAX_PDFS} PDFs supported.")
            return
        self.pdfs.append(None)
        self._update_geometry()
        self._refresh_slots()

    def remove_last_slot(self):
        if len(self.pdfs) <= MIN_PDFS:
            return
        self.pdfs.pop()
        self._update_geometry()
        self._refresh_slots()

    def _refresh_slots(self):
        self._render_slots()
        self._refresh_buttons()

    def _refresh_buttons(self):
        n = len(self.pdfs)
        self.btn_add.config(state="normal" if n < MAX_PDFS else "disabled")
        self.btn_remove.config(state="normal" if n > MIN_PDFS else "disabled")

    # ============== MERGE ==============

    def start_merge(self):
        filled = [p for p in self.pdfs if p]
        if len(filled) < MIN_PDFS:
            messagebox.showerror(
                "Error", f"Please select at least {MIN_PDFS} PDFs to merge."
            )
            return

        self._merge_list = filled
        base_name = f"merged_{os.path.splitext(os.path.basename(filled[0]))[0]}.pdf"
        default_dir = os.path.dirname(filled[0])

        save_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=base_name,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not save_path:
            return

        output_path = self._get_unique_filename(save_path)

        self.merge_button.config(state="disabled")
        self.btn_add.config(state="disabled")
        self.btn_remove.config(state="disabled")
        self.status_label.config(text="Merging PDFs...")
        self.progress["value"] = 0
        self.progress.start(10)

        threading.Thread(
            target=self._merge_worker, args=(output_path,), daemon=True
        ).start()

    def _merge_worker(self, output_path):
        try:
            from PyPDF2 import PdfMerger

            paths = self._merge_list
            total = len(paths)
            logging.info(f"Merging {total} PDFs -> {output_path}")
            for i, p in enumerate(paths):
                logging.info(f"  [{i + 1}] {p}")

            merger = PdfMerger()

            for i, path in enumerate(paths):
                pct = int((i / total) * 90)
                label = f"Reading PDF {i + 1} of {total}..."
                self.root.after(
                    0,
                    lambda l=label, v=pct: (
                        self.status_label.config(text=l),
                        self.progress.config(value=v),
                    ),
                )
                merger.append(path)

            self.root.after(
                0,
                lambda: (
                    self.status_label.config(text="Writing output file..."),
                    self.progress.config(value=90),
                ),
            )
            merger.write(output_path)
            merger.close()

            logging.info("Merge completed successfully.")
            self.root.after(0, self._merge_success)

        except Exception:
            logging.exception("Merge failed")
            self.root.after(0, self._merge_failed)

    def _merge_success(self):
        self.progress["value"] = 100
        self.progress.stop()
        self.status_label.config(text="Merge completed")
        messagebox.showinfo("Success", "PDFs merged successfully!")
        self.root.destroy()

    def _merge_failed(self):
        self.progress["value"] = 0
        self.progress.stop()
        self.status_label.config(text="Merge failed")
        self.merge_button.config(state="normal")
        self._refresh_buttons()
        messagebox.showerror(
            "Error",
            f"Failed to merge PDFs.\n\nA log file has been created:\n{LOG_FILE}",
        )

    # ============== UTILS ==============

    def _get_unique_filename(self, path):
        if not os.path.exists(path):
            return path
        base, ext = os.path.splitext(path)
        counter = 1
        while True:
            new_path = f"{base}[{counter}]{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1


# ================= MAIN =================


def main():
    initial_files = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")]

    if initial_files:
        logging.info(f"Launched with {len(initial_files)} PDF(s) via argv.")
    else:
        logging.info("Launched manually (no argv PDFs).")

    root = create_root_window()
    if len(initial_files) > MAX_PDFS:
        root.withdraw()
        messagebox.showerror("Merge PDFs", f"Select at most {MAX_PDFS} PDFs.", parent=root)
        root.destroy()
        return

    def safe_exit(event=None):
        logging.info("Application closed by user")
        root.destroy()

    root.bind("<Escape>", safe_exit)
    root.protocol("WM_DELETE_WINDOW", safe_exit)

    PDFMergerApp(root, initial_files if initial_files else None)
    root.mainloop()


if __name__ == "__main__":
    main()
