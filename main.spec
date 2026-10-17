# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('styles', 'styles'), ('resources', 'resources')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('babelfish')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('guessit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


import os

# Gets the path to the folder where this .spec file is located
work_dir = os.path.abspath(os.getcwd())

def create_constants_file(is_portable):
    with open("build_constants.py", "w") as f:
        f.write(f"IS_PORTABLE = {is_portable}")

def get_analysis(is_portable):
    create_constants_file(is_portable)
    return Analysis(
    [os.path.join(work_dir, 'main.py')],
    pathex=[work_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.QtCharts', 'PySide6.QtDataVisualization', 'PySide6.QtBluetooth', 'PySide6.QtMultimedia', 'PySide6.QtQuick', 'PySide6.QtNetwork'],
    noarchive=False,
    optimize=0,
    )

# STANDARD Release
a_port = get_analysis(is_portable=False)
pyz_port = PYZ(a_port.pure)
exe_port = EXE(
    pyz_port,
    a_port.scripts,
    a_port.binaries,
    a_port.datas,
    [],
    name='Simpler-FileBot',
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

# PORTABLE Release
a_port = get_analysis(is_portable=True)
pyz_port = PYZ(a_port.pure)
exe_port = EXE(
    pyz_port,
    a_port.scripts,
    a_port.binaries,
    a_port.datas,
    [],
    name='Simpler-FileBot-Portable',
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

# --- CLEANUP ---
# remove TEMP after build.
if os.path.exists("build_constants.py"):
    os.remove("build_constants.py")
