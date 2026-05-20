"""
dpi_utils — Détection DPI et moniteur courant via Windows API (ctypes).

Fournit des informations fiables sur le moniteur contenant la fenêtre :
  - Position et dimensions de la work area (exclut taskbar)
  - Facteur de scale DPI (1.0 = 96dpi, 1.25 = 120dpi, etc.)
"""

import ctypes
import ctypes.wintypes as wintypes
from dataclasses import dataclass

# ── Constantes Windows ────────────────────────────────────────
MONITOR_DEFAULTTONEAREST = 2
MDT_EFFECTIVE_DPI = 0


@dataclass
class MonitorInfo:
    """Informations sur un moniteur."""
    x: int          # left de la work area (pixels physiques)
    y: int          # top de la work area
    width: int      # largeur work area
    height: int     # hauteur work area
    scale: float    # facteur DPI (1.0, 1.25, 1.5, 2.0...)


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def get_hwnd(tk_window) -> int:
    """Récupère le HWND natif d'une fenêtre Tk/CTk toplevel."""
    # winfo_id() retourne le frame interne ; on veut le toplevel
    # wm_frame() retourne le HWND du frame WM sous forme de string hex
    frame_id = tk_window.wm_frame()
    if isinstance(frame_id, str):
        return int(frame_id, 16) if frame_id.startswith("0x") else int(frame_id)
    return int(frame_id)


def get_monitor_info(tk_window) -> MonitorInfo:
    """
    Retourne les infos du moniteur contenant la fenêtre tk_window.
    
    Utilise MonitorFromWindow + GetMonitorInfo pour la work area,
    et GetDpiForMonitor (shcore) pour le facteur de scale.
    
    Fallback robuste si les APIs ne sont pas disponibles.
    """
    try:
        hwnd = get_hwnd(tk_window)
    except Exception:
        hwnd = 0

    user32 = ctypes.windll.user32

    # Obtenir le handle du moniteur
    hmonitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

    # Obtenir la work area
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hmonitor, ctypes.byref(mi))

    work = mi.rcWork
    x = work.left
    y = work.top
    width = work.right - work.left
    height = work.bottom - work.top

    # Obtenir le DPI du moniteur
    scale = _get_monitor_scale(hmonitor)

    return MonitorInfo(x=x, y=y, width=width, height=height, scale=scale)


def _get_monitor_scale(hmonitor) -> float:
    """Récupère le facteur de scale DPI pour un moniteur donné."""
    # Méthode 1 : GetDpiForMonitor (Windows 8.1+, shcore.dll)
    try:
        shcore = ctypes.windll.shcore
        dpi_x = ctypes.c_uint()
        dpi_y = ctypes.c_uint()
        hr = shcore.GetDpiForMonitor(
            hmonitor, MDT_EFFECTIVE_DPI,
            ctypes.byref(dpi_x), ctypes.byref(dpi_y)
        )
        if hr == 0:  # S_OK
            return dpi_x.value / 96.0
    except (OSError, AttributeError):
        pass

    # Méthode 2 : GetDeviceCaps (fallback, DPI système global)
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except Exception:
        pass

    return 1.0
