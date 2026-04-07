# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import customtkinter

# ── Assets customtkinter (fonts, thèmes JSON) ─────────────────
ctk_path = Path(customtkinter.__file__).parent

# ── Tcl/Tk : chemin calculé dynamiquement depuis l'exe Python ─
# Structure standard : <python_root>/tcl/tcl8.6  et  <python_root>/tcl/tk8.6
python_root = Path(sys.executable).parent
tcl_root = python_root / 'tcl'

datas = [
    (str(ctk_path / 'assets'), 'customtkinter/assets'),
]

# Inclure tcl8.6 et tk8.6 s'ils existent (Windows)
# PyInstaller (_tkinter) cherche Tcl dans _tcl_data et Tk dans _tk_data
if (tcl_root / 'tcl8.6').exists():
    datas.append((str(tcl_root / 'tcl8.6'), '_tcl_data'))
if (tcl_root / 'tk8.6').exists():
    datas.append((str(tcl_root / 'tk8.6'), '_tk_data'))

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
    runtime_hooks=[],
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
