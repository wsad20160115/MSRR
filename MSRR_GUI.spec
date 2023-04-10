# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['MSRR_GUI.py', 'tag.py'],
    pathex=['G:\\我的雲端硬碟\\NTUT\\code\\MSRR_GUI'],
    binaries=[],
    datas=[],
    hiddenimports=['G:\\我的雲端硬碟\\NTUT\\code\\MSRR_GUI'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MSRR_GUI',
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
    icon=['ACTL72.ico'],
)
