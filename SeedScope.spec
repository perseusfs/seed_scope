# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['script.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('germination_data.xlsx', '.'),
        ('mass_data.xlsx', '.'),
        ('length_data.xlsx', '.'),
        ('germination_data_treat_diff.xlsx', '.'),
        ('sprout.png', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ONEFILE: binaries/zipfiles/datas dogrudan EXE icine konur, COLLECT YOK
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SeedScope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,            # PyQt5 ile UPX bazen exe'yi bozar; kapali daha guvenli
    runtime_tmpdir=None,
    console=False,
    icon='sprout.png',    # Windows ikon icin .ico gerekir (png'yi cevir)
)
