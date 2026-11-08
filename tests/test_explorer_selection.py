"""Exercise the merge verb with real Windows Shell selection data."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pythoncom
from win32com.server.util import wrap
from win32com.shell import shell, shellcon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import merge_launcher


class ExplorerSelectionTest(unittest.TestCase):
    def test_each_drop_opens_one_window_with_its_own_complete_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = shell.SHGetDesktopFolder().BindToObject(
                shell.SHParseDisplayName(tmp, 0)[0], None, shell.IID_IShellFolder
            )
            paths = []
            for n in range(6):
                path = Path(tmp, f"résumé ({n}).pdf")
                path.touch()
                paths.append(str(path))
            target = wrap(merge_launcher.MergeDropTarget(), pythoncom.IID_IDropTarget)
            with patch.object(merge_launcher, "launch_merge", return_value=True) as launch:
                for selection in (paths[:5], paths[5:], paths[::-1]):
                    children = [shell.SHParseDisplayName(p, 0)[0][-1:] for p in selection]
                    _, data = folder.GetUIObjectOf(0, children, pythoncom.IID_IDataObject)
                    target.Drop(data, 0, (0, 0), shellcon.DROPEFFECT_COPY)
                    launch.assert_called_once_with(selection)
                    launch.reset_mock()

    def test_over_limit_does_not_launch_a_partial_merge(self):
        with patch.object(merge_launcher.win32api, "MessageBox") as warning, \
             patch.object(merge_launcher.subprocess, "Popen") as popen:
            self.assertFalse(merge_launcher.launch_merge(["sample.pdf"] * 7))
            warning.assert_called_once()
            popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
