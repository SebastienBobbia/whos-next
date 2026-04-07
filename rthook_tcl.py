"""
Runtime hook — force TCL_LIBRARY et TK_LIBRARY vers _tcl_data/_tk_data
packagés dans le bundle PyInstaller (one-file exe).
"""
import os
import sys

_base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

_tcl = os.path.join(_base, '_tcl_data')
_tk  = os.path.join(_base, '_tk_data')

if os.path.isdir(_tcl):
    os.environ['TCL_LIBRARY'] = _tcl

if os.path.isdir(_tk):
    os.environ['TK_LIBRARY'] = _tk
