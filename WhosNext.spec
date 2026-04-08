# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import customtkinter

# ── Assets customtkinter (fonts, thèmes JSON) ─────────────────
ctk_path = Path(customtkinter.__file__).parent

datas = [
    (str(ctk_path / 'assets'), 'customtkinter/assets'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        '_tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageFile',
        'PIL.ImageMode',
        'PIL.ImagePalette',
        'PIL.ImageOps',
        'PIL.ImageFilter',
        'PIL.PngImagePlugin',
        'PIL.JpegImagePlugin',
        'PIL.BmpImagePlugin',
        'PIL.GifImagePlugin',
        'PIL.WebPImagePlugin',
        'PIL.IcoImagePlugin',
        'cairosvg',
        'cairocffi',
        'cssselect2',
        'tinycss2',
        'defusedxml',
        'webencodings',
        'customtkinter',
        'darkdetect',
        'darkdetect._linux_detect',
        'darkdetect._windows_detect',
        'darkdetect._mac_detect',
        'packaging',
        'packaging.version',
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

# Mode one-folder : crée dist/WhosNext/ avec WhosNext.exe + tous les fichiers
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhosNext',
)
