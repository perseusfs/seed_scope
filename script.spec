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
        ('sprout.png', '.')
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SeedScope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='sprout.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='SeedScope',
)