# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import customtkinter

# ── Assets customtkinter (fonts, thèmes JSON) ─────────────────
ctk_path = Path(customtkinter.__file__).parent

datas = [
    (str(ctk_path / 'assets'), 'customtkinter/assets'),
    ('default_data', 'default_data'),
    ('assets', 'assets'),
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
        'darkdetect._windows_detect',
        'packaging',
        'packaging.version',
        'collections',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Modules inutiles sur Windows (réduisent le nombre de fichiers)
        'darkdetect._linux_detect',
        'darkdetect._mac_detect',
        'setuptools',
        # distutils est requis par setuptools — ne pas exclure
        # ast est requis par inspect — ne pas exclure

        'py_compile',
        'compileall',
        'zipimport',
        'tarfile',
        'csv',
        'calendar',
        'curses',
        'readline',
        'rlcompleter',
        'antigravity',
        'this',
        'turtle',
        'turtledemo',
    ],
    noarchive=False,
    optimize=1,
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
    upx=False,          # UPX désactivé : décompression = lenteur au démarrage
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',
)

# Mode one-folder : crée dist/WhosNext/ avec WhosNext.exe + tous les fichiers
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,          # UPX désactivé sur les DLLs aussi
    upx_exclude=[],
    name='WhosNext',
)
