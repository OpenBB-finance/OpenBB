# -*- mode: python ; coding: utf-8 -*-  # noqa
import os
import subprocess
import sys
from pathlib import Path
import matplotlib

import scipy
from dotenv import set_key
from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.splash import Splash
from PyInstaller.compat import is_darwin, is_win

from openbb_terminal.loggers import get_commit_hash

NAME = "OpenBBTerminal"

build_type = (
    os.getenv("OPENBB_BUILD_TYPE") if bool(os.getenv("OPENBB_BUILD_TYPE")) else "folder"
)
repo_path = Path(os.getcwd()).resolve()

# Local python environment packages folder
venv_path = Path(sys.executable).parent.parent.resolve()

# Check if we are running in a conda environment
if is_darwin:
    pathex = os.path.join(os.path.dirname(os.__file__), "site-packages")
else:
    if "site-packages" in list(venv_path.iterdir()):
        pathex = str(venv_path / "site-packages")
    else:
        pathex = str(venv_path / "lib" / "site-packages")

pathex = Path(pathex).resolve()

# Removing unused ARM64 binary
binary_to_remove = pathex / "_scs_direct.cpython-39-darwin.so"
print("Removing ARM64 Binary: _scs_direct.cpython-39-darwin.so")
binary_to_remove.unlink(missing_ok=True)
build_assets_folder = repo_path / "build/pyinstaller"

# Removing inspect hook
destination = pathex / "pyinstaller/hooks/rthooks/pyi_rth_inspect.py"
print("Replacing Pyinstaller Hook: pyi_rth_inspect.py")
source = build_assets_folder / "hooks/pyi_rth_inspect.py"
subprocess.run(["cp", str(source), str(destination)], check=True)


# Get latest commit
commit_hash = get_commit_hash()
default_env_file = build_assets_folder / ".env"
set_key(default_env_file, "OPENBB_LOGGING_COMMIT_HASH", str(commit_hash))

# Files that are explicitly pulled into the bundle
added_files = [
    (str(repo_path / "openbb_terminal"), "openbb_terminal"),
    (str(repo_path / "openbb_terminal/core/plots"), "openbb_terminal/core/plots"),
    (str(pathex / "property_cached"), "property_cached"),
    (str(pathex / "user_agent"), "user_agent"),
    (str(pathex / "vaderSentiment"), "vaderSentiment"),
    (str(pathex / "prophet"), "prophet"),
    (str(pathex / "whisper"), "whisper"),
    (str(pathex / "transformers"), "transformers"),
    (str(pathex / "linearmodels/datasets"), "./linearmodels/datasets"),
    (str(pathex / "statsmodels/datasets"), "./statsmodels/datasets"),
    (str(pathex / "debugpy/_vendored"), "./debugpy/_vendored"),
    (".env", "."),
    (str(pathex / "blib2to3/Grammar.txt"), "blib2to3"),
    (str(pathex / "blib2to3/PatternGrammar.txt"), "blib2to3"),
    (str(pathex / "streamlit"), "streamlit"),
    (str(pathex / "altair"), "altair"),
    (str(pathex / "pyarrow"), "pyarrow"),
    (str(pathex / "langchain"), "langchain"),
    (str(pathex / "llama_index/VERSION"), "llama_index"),
    (str(pathex / "tiktoken"), "tiktoken"),
    (str(pathex / "tiktoken_ext"), "tiktoken_ext"),
]

if is_win:
    added_files.extend(
        [
            (os.path.join(f"{os.path.dirname(scipy.__file__)}.libs"), "scipy.libs/"),
            (str(pathex / "frozendict/version.py"), "frozendict"),
            (
                os.path.join(f"{os.path.dirname(matplotlib.__file__)}.libs"),
                "matplotlib.libs/",
            ),
        ]
    )


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
    "feedparser",
    "_sysconfigdata__darwin_darwin",
    "prophet",
    "debugpy",
    "pywry.pywry",
    "scipy.sparse.linalg._isolve._iterative",
    "whisper",
    "transformers",
    "yt_dlp",
    "textwrap3",
    "streamlit",
    "pytrends",
    "pytrends.request",
    "pyarrow",
    "langchain",
]


if is_win:
    hidden_imports.append("frozendict")

analysis_kwargs = dict(
    scripts=[str(repo_path / "terminal.py")],
    pathex=[str(pathex), "."],
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

# Executable icon
if is_win:
    exe_icon = (str(repo_path / "images/openbb_icon.ico"),)
if is_darwin:
    exe_icon = (str(repo_path / "images/openbb.icns"),)

block_cipher = None
# PyWry
pywry_a = Analysis(
    [str(pathex / "pywry/backend.py")],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pywry_pyz = PYZ(pywry_a.pure, pywry_a.zipped_data, cipher=block_cipher)


# PyWry EXE
pywry_exe = EXE(
    pywry_pyz,
    pywry_a.scripts,
    [],
    exclude_binaries=True,
    name="OpenBBPlotsBackend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=True,
    disable_windowed_traceback=False,
    target_arch="x86_64",
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
)

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
    icon=exe_icon,
    version="version.rc",
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
        str(repo_path / "images/openbb_splashscreen.png"),
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(200, 400),
        text_size=12,
        text_color="white",
    )
    exe_args += [splash, splash.binaries]

if is_darwin:
    exe_kwargs["argv_emulation"] = True

exe = EXE(*exe_args, **exe_kwargs)
pywry_collect_args = [
    pywry_a.binaries,
    pywry_a.zipfiles,
    pywry_a.datas,
]

if build_type == "folder":
    coll = COLLECT(
        *([exe] + collect_args + [pywry_exe] + pywry_collect_args),
        **collect_kwargs,
    )
