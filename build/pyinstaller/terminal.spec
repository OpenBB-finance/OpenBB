# -*- mode: python ; coding: utf-8 -*-
import os
import sys

pathex = os.path.join(
    os.path.dirname(sys.executable), "..", "lib", "python3.8", "site-packages"
)

block_cipher = None

added_files = [
    (os.path.join(os.getcwd(), "gamestonk_terminal"), "gamestonk_terminal"),
    (os.path.join(os.getcwd(), "routines"), "routines"),
    (os.path.join(os.getcwd(), "styles"), "styles"),
    (
        os.path.join("frozendict", "VERSION"),
        "frozendict",
    ),
]
a = Analysis(
    [os.path.join(os.getcwd(), "terminal.py")],
    pathex=[pathex, "."],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        "sklearn.utils._cython_blas",
        "sklearn.utils._typedefs",
        "sklearn.neighbors.quad_tree",
        "sklearn.tree._utils",
        "sklearn.neighbors._partition_nodes",
        "squarify",
        "linearmodels",
        "user_agent",
        "vaderSentiment",
        "frozendict",
        "boto3",
        "textwrap3",
        "pyEX",
    ],
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
    name="terminal",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch="x86_64",
    codesign_identity=None,
    entitlements_file=None,
)


# exe = EXE(
#     pyz,
#     a.scripts,
#     [],
#     exclude_binaries=True,
#     name="terminal",
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     console=True,
#     disable_windowed_traceback=False,
#     target_arch="x86_64",
#     codesign_identity=None,
#     entitlements_file=None,
# )
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name="terminal",
# )
