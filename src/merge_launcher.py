import logging
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pythoncom
import win32api
import win32con
from win32com.server import localserver, policy  # policy is loaded dynamically by pythoncom
from win32com.shell import shell, shellcon

from merge_selection import MAX_PDFS


CLSID = "{C25FF893-9205-476D-8249-930868447218}"
HDROP_FORMAT = (win32con.CF_HDROP, None, pythoncom.DVASPECT_CONTENT, -1, pythoncom.TYMED_HGLOBAL)


def launch_merge(paths):
    if len(paths) > MAX_PDFS:
        win32api.MessageBox(0, f"Select at most {MAX_PDFS} PDFs to merge.", "Merge PDFs",
                            win32con.MB_ICONINFORMATION)
        return False
    logging.info("Opening one merge window with %d PDF(s): %r", len(paths), paths)
    app = Path(sys.executable).with_name("merge_app.exe")
    subprocess.Popen([str(app), *paths], close_fds=True)
    return True


class MergeDropTarget:
    """Explorer calls Drop once with the data object for this menu invocation."""

    _com_interfaces_ = [pythoncom.IID_IDropTarget]
    _public_methods_ = ["DragEnter", "DragOver", "DragLeave", "Drop"]

    def DragEnter(self, data, keys, point, effect):
        return effect & shellcon.DROPEFFECT_COPY

    def DragOver(self, keys, point, effect):
        return effect & shellcon.DROPEFFECT_COPY

    def DragLeave(self):
        pass

    def Drop(self, data, keys, point, effect):
        try:
            medium = data.GetData(HDROP_FORMAT)
            count = shell.DragQueryFile(medium.data_handle, -1)
            paths = [shell.DragQueryFile(medium.data_handle, i) for i in range(count)]
            if not paths or any(not p.lower().endswith(".pdf") for p in paths):
                raise ValueError("Select PDF files in File Explorer.")
            if launch_merge(paths):
                return effect & shellcon.DROPEFFECT_COPY
        except Exception as exc:
            logging.exception("Could not open Explorer selection")
            win32api.MessageBox(0, str(exc), "Merge PDFs", win32con.MB_ICONERROR)
        return shellcon.DROPEFFECT_NONE


def main():
    log_dir = Path(os.getenv("LOCALAPPDATA", ".")) / "PDFTools" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=log_dir / f"merge_launcher_{date.today()}.log",
                        level=logging.INFO, encoding="utf-8",
                        format="%(asctime)s | %(levelname)s | %(message)s")
    if any(arg.lower() in ("-embedding", "/embedding") for arg in sys.argv[1:]):
        localserver.serve([CLSID])
    else:
        launch_merge([arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")])


if __name__ == "__main__":
    main()
