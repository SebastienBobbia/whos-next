# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import customtkinter

# ── Assets customtkinter (fonts, thèmes JSON) ─────────────────
ctk_path = Path(customtkinter.__file__).parent

datas = [
    (str(ctk_path / 'assets'), 'customtkinter/assets'),
]

# NOTE: Tcl/Tk est géré automatiquement par le hook PyInstaller (hook-_tkinter.py)
# Ne pas l'inclure manuellement ici pour éviter les conflits cross-platform.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Tkinter
        'tkinter',
        '_tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # Pillow — modules de base
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageFile',
        'PIL.ImageMode',
        'PIL.ImagePalette',
        'PIL.ImageOps',
        'PIL.ImageFilter',
        # Pillow — plugins format image (chargés dynamiquement à runtime)
        'PIL.PngImagePlugin',
        'PIL.JpegImagePlugin',
        'PIL.BmpImagePlugin',
        'PIL.GifImagePlugin',
        'PIL.WebPImagePlugin',
        'PIL.IcoImagePlugin',
        # customtkinter
        'customtkinter',
        # darkdetect (dépendance customtkinter, sous-modules conditionnels par OS)
        'darkdetect',
        'darkdetect._linux_detect',
        'darkdetect._windows_detect',
        'darkdetect._mac_detect',
        # packaging (utilisé par customtkinter pour comparer les versions)
        'packaging',
        'packaging.version',
        # stdlib
        'collections',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rthook_tcl.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WhosNext',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
