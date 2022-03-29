# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import json

from PyInstaller.compat import is_darwin, is_win
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.splash import Splash
from PyInstaller.building.build_main import Analysis

from openbb_terminal.loggers import get_commit_hash

NAME = "OpenBBTerminal"

build_type = (
    os.getenv("OPENBB_BUILD_TYPE") if bool(os.getenv("OPENBB_BUILD_TYPE")) else "folder"
)

# Local python environment packages folder
pathex = os.path.join(
    os.path.dirname(sys.executable), "..", "lib", "python3.8", "site-packages"
)

# Get latest commit
commit_hash = get_commit_hash()
build_assets_folder = os.path.join(os.getcwd(), "build", "pyinstaller")
default_feature_flags_path = os.path.join(build_assets_folder, "OBBFF_DEFAULTS.json")
with open(default_feature_flags_path, "r") as f:
    default_gtff = json.load(f)

default_gtff["OBBFF_LOGGING_COMMIT_HASH"] = commit_hash
with open(default_feature_flags_path, "w") as f:
    json.dump(default_gtff, f, indent=4)

# Files that are explicitly pulled into the bundle
added_files = [
    (os.path.join(os.getcwd(), "openbb_terminal"), "openbb_terminal"),
    (os.path.join(os.getcwd(), "routines"), "routines"),
    (os.path.join(os.getcwd(), "styles"), "styles"),
    ("property_cached", "property_cached"),
    ("user_agent", "user_agent"),
    ("vaderSentiment", "vaderSentiment"),
    (
        os.path.join("frozendict", "VERSION"),
        "frozendict",
    ),
    ("OBBFF_DEFAULTS.json", "openbb_terminal"),
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
    "tensorflow",
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
        os.path.join(os.getcwd(), "images", "splashscreen.png"),
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(200, 400),
        text_size=12,
        text_color="white",
    )
    exe_args += [splash, splash.binaries]
    exe_kwargs["icon"] = (os.path.join(os.getcwd(), "images", "gst_app.ico"),)

if is_darwin:
    exe_kwargs["icon"] = (
        os.path.join(os.getcwd(), "images", "GamestonkTerminal.icns"),
    )

exe = EXE(*exe_args, **exe_kwargs)

if build_type == "folder":
    coll = COLLECT(*([exe] + collect_args), **collect_kwargs)
