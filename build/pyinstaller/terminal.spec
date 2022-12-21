# -*- mode: python ; coding: utf-8 -*-
import os
import pathlib
import subprocess

from dotenv import set_key

from PyInstaller.compat import is_darwin, is_win
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.splash import Splash
from PyInstaller.building.build_main import Analysis


# import subprocess

from openbb_terminal.loggers import get_commit_hash

NAME = "OpenBBTerminal"

build_type = (
    os.getenv("OPENBB_BUILD_TYPE") if bool(os.getenv("OPENBB_BUILD_TYPE")) else "folder"
)

# Local python environment packages folder
pathex = os.path.join(os.path.dirname(os.__file__), "site-packages")

# Removing unused ARM64 binary
binary_to_remove = pathlib.Path(
    os.path.join(pathex, "_scs_direct.cpython-39-darwin.so")
)
print("Removing ARM64 Binary: _scs_direct.cpython-39-darwin.so")
binary_to_remove.unlink(missing_ok=True)

# Removing inspect hook
destination = pathlib.Path(
    os.path.join(pathex, "pyinstaller/hooks/rthooks", "pyi_rth_inspect.py")
)
print("Replacing Pyinstaller Hook: pyi_rth_inspect.py")
source = "build/pyinstaller/hooks/pyi_rth_inspect.py"
subprocess.run(["cp", source, str(destination)], check=True)


# Get latest commit
commit_hash = get_commit_hash()
build_assets_folder = os.path.join(os.getcwd(), "build", "pyinstaller")
default_env_file = os.path.join(build_assets_folder, ".env")
set_key(default_env_file, "OPENBB_LOGGING_COMMIT_HASH", str(commit_hash))

# Files that are explicitly pulled into the bundle
added_files = [
    (os.path.join(os.getcwd(), "openbb_terminal"), "openbb_terminal"),
    (os.path.join(pathex, "property_cached"), "property_cached"),
    (os.path.join(pathex, "user_agent"), "user_agent"),
    (os.path.join(pathex, "vaderSentiment"), "vaderSentiment"),
    (os.path.join(pathex, "prophet"), "prophet"),
    (os.path.join(pathex, "frozendict", "VERSION"), "frozendict"),
    (
        os.path.join(pathex, "linearmodels", "datasets"),
        os.path.join("linearmodels", "datasets"),
    ),
    (
        os.path.join(pathex, "statsmodels", "datasets"),
        os.path.join("statsmodels", "datasets"),
    ),
    (
        os.path.join(pathex, "investpy", "resources"),
        os.path.join("investpy", "resources"),
    ),
    (
        os.path.join(pathex, "debugpy", "_vendored"),
        os.path.join("debugpy", "_vendored"),
    ),
    (".env", "."),
    (os.path.join(pathex, "blib2to3", "Grammar.txt"), "blib2to3"),
    (os.path.join(pathex, "blib2to3", "PatternGrammar.txt"), "blib2to3"),
]

# Python libraries that are explicitly pulled into the bundle
hidden_imports = [
    "sklearn.utils._cython_blas",
    "sklearn.utils._typedefs",
    "sklearn.utils._heap",
    "sklearn.utils._sorting",
    "sklearn.utils._vector_sentinel",
    "sklearn.neighbors.quad_tree",
    "sklearn.tree._utils",
    "sklearn.neighbors._partition_nodes",
    "sklearn.metrics._pairwise_distances_reduction._datasets_pair",
    "sklearn.metrics._pairwise_distances_reduction._middle_term_computer",
    "squarify",
    "linearmodels",
    "statsmodels",
    "user_agent",
    "vaderSentiment",
    "frozendict",
    "textwrap3",
    "pyEX",
    "feedparser",
    "_sysconfigdata__darwin_darwin",
    "prophet",
    "debugpy",
]


analysis_kwargs = dict(
    scripts=[os.path.join(os.getcwd(), "terminal.py")],
    pathex=[pathex, "."],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=["build/pyinstaller/hooks"],
    hooksconfig={},
    runtime_hooks=["build/pyinstaller/hooks/hook-debugpy.py"],
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
        os.path.join(os.getcwd(), "images", "openbb_splashscreen.png"),
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(200, 400),
        text_size=12,
        text_color="white",
    )
    exe_args += [splash, splash.binaries]
    exe_kwargs["icon"] = (os.path.join(os.getcwd(), "images", "openbb_icon.ico"),)

if is_darwin:
    exe_kwargs["icon"] = (os.path.join(os.getcwd(), "images", "openbb.icns"),)

exe = EXE(*exe_args, **exe_kwargs)

if build_type == "folder":
    coll = COLLECT(*([exe] + collect_args), **collect_kwargs)
