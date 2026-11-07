"""Test module for verifying win32 dependency imports."""

import pywintypes
import win32file
import win32pipe


def test_win32_imports():
    assert win32pipe is not None
    assert win32file is not None
    assert pywintypes is not None
    print(f"win32pipe version: {win32pipe.__version__}")


if __name__ == "__main__":
    test_win32_imports()
