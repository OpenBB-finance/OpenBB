# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.compat import is_darwin, is_win
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.splash import Splash
from PyInstaller.building.build_main import Analysis

NAME = "GamestonkTerminal"

build_type = (
    os.getenv("GT_BUILD_TYPE") if bool(os.getenv("GT_BUILD_TYPE")) else "folder"
)

# Local python environment packages folder
pathex = os.path.join(
    os.path.dirname(sys.executable), "..", "lib", "python3.8", "site-packages"
)

# Files that are explicitly pulled into the bundle
added_files = [
    (os.path.join(os.getcwd(), "gamestonk_terminal"), "gamestonk_terminal"),
    (os.path.join(os.getcwd(), "routines"), "routines"),
    (os.path.join(os.getcwd(), "styles"), "styles"),
    (
        os.path.join("frozendict", "VERSION"),
        "frozendict",
    ),
    ("GTFF_DEFAULTS.json", "gamestonk_terminal"),
]

# Python libraries that are explicitly pulled into the bundle
hidden_imports = [
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
]

analysis_kwargs = dict(
    scripts=[os.path.join(os.getcwd(), "terminal.py")],
    pathex=[pathex, "."],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

a = Analysis(**analysis_kwargs)
pyz = PYZ(a.pure, a.zipped_data, cipher=analysis_kwargs["cipher"])

exe_args = [
    pyz,
    a.scripts,
    [],
]

exe_kwargs = dict(
    name=NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    console=True,
    disable_windowed_traceback=False,
    target_arch="x86_64",
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(os.getcwd(), "..", "..", "images", "gst_app.ico"),
)

# Packaging settings
if build_type == "onefile":
    exe_args += [a.binaries, a.zipfiles, a.datas]
    exe_kwargs["runtime_tmpdir"] = None
elif build_type == "folder":
    exe_kwargs["exclude_binaries"] = True
    collect_args = [
        a.binaries,
        a.zipfiles,
        a.datas,
    ]
    collect_kwargs = dict(
        strip=False,
        upx=True,
        upx_exclude=[],
        name=NAME,
    )


# Platform specific settings
if is_win:
    splash = Splash(
        os.path.join(os.getcwd(), "..", "..", "images", "splashscreen.png"),
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(200, 400),
        text_size=12,
        text_color="white",
    )
    exe_args += [splash, splash.binaries]

if is_darwin:
    pass

exe = EXE(*exe_args, **exe_kwargs)

if build_type == "folder":
    coll = COLLECT(*([exe] + collect_args), **collect_kwargs)
