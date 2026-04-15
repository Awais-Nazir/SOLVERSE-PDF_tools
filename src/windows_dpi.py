import ctypes
import sys
import tkinter as tk


PER_MONITOR_AWARE_V2 = -4
PROCESS_PER_MONITOR_DPI_AWARE = 2
S_OK = 0
E_ACCESSDENIED = 0x80070005
SIGNED_E_ACCESSDENIED = -2147024891


def configure_windows_dpi_awareness(platform=sys.platform, ctypes_module=ctypes):
    if platform != "win32":
        return False

    windll = getattr(ctypes_module, "windll", None)
    if windll is None:
        return False

    try:
        user32 = getattr(windll, "user32", None)
    except OSError:
        user32 = None

    try:
        shcore = getattr(windll, "shcore", None)
    except OSError:
        shcore = None

    if user32 is not None:
        set_dpi_context = getattr(user32, "SetProcessDpiAwarenessContext", None)
        if set_dpi_context is not None:
            if set_dpi_context(ctypes_module.c_void_p(PER_MONITOR_AWARE_V2)):
                return True

    if shcore is not None:
        set_dpi_awareness = getattr(shcore, "SetProcessDpiAwareness", None)
        if set_dpi_awareness is not None:
            result = set_dpi_awareness(PROCESS_PER_MONITOR_DPI_AWARE)
            if result in (S_OK, E_ACCESSDENIED, SIGNED_E_ACCESSDENIED):
                return True

    if user32 is not None:
        set_dpi_aware = getattr(user32, "SetProcessDPIAware", None)
        if set_dpi_aware is not None:
            return bool(set_dpi_aware())

    return False


def create_root_window(tk_module=tk, platform=sys.platform, ctypes_module=ctypes):
    configure_windows_dpi_awareness(
        platform=platform,
        ctypes_module=ctypes_module,
    )
    return tk_module.Tk()
