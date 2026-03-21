"""Install for development script."""

# flake8: noqa: S603

from __future__ import annotations

import importlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

PLATFORM_PATH = Path(__file__).parent.resolve()
LOCK = PLATFORM_PATH / "poetry.lock"
PYPROJECT = PLATFORM_PATH / "pyproject.toml"
CLI_PATH = Path(__file__).parent.parent.resolve() / "cli"
CLI_PYPROJECT = CLI_PATH / "pyproject.toml"
CLI_LOCK = CLI_PATH / "poetry.lock"

LOCAL_DEPS = """
[tool.poetry.dependencies]
python = ">=3.10,<3.14"
openbb-devtools = { path = "./extensions/devtools", develop = true, markers = "python_version >= '3.10'" }
openbb-core = { path = "./core", develop = true }
openbb-platform-api = { path = "./extensions/platform_api", develop = true }

openbb-benzinga = { path = "./providers/benzinga", develop = true }
openbb-bls = { path = "./providers/bls", develop = true }
openbb-cftc = { path = "./providers/cftc", develop = true }
openbb-congress-gov = { path = "./providers/congress_gov", develop = true }
openbb-econdb = { path = "./providers/econdb", develop = true }
openbb-federal-reserve = { path = "./providers/federal_reserve", develop = true }
openbb-fmp = { path = "./providers/fmp", develop = true }
openbb-fred = { path = "./providers/fred", develop = true }
openbb-government-us = { path = "./providers/government_us", develop = true }
openbb-imf = { path = "./providers/imf", develop = true }
openbb-intrinio = { path = "./providers/intrinio", develop = true }
openbb-oecd = { path = "./providers/oecd", develop = true }
openbb-sec = { path = "./providers/sec", develop = true }
openbb-tiingo = { path = "./providers/tiingo", develop = true }
openbb-tradingeconomics = { path = "./providers/tradingeconomics", develop = true }
openbb-us-eia = { path = "./providers/eia", develop = true }
openbb-yfinance = { path = "./providers/yfinance", develop = true }

openbb-commodity = { path = "./extensions/commodity", develop = true }
openbb-crypto = { path = "./extensions/crypto", develop = true }
openbb-currency = { path = "./extensions/currency", develop = true }
openbb-derivatives = { path = "./extensions/derivatives", develop = true }
openbb-economy = { path = "./extensions/economy", develop = true }
openbb-equity = { path = "./extensions/equity", develop = true }
openbb-etf = { path = "./extensions/etf", develop = true }
openbb-fixedincome = { path = "./extensions/fixedincome", develop = true }
openbb-index = { path = "./extensions/index", develop = true }
openbb-news = { path = "./extensions/news", develop = true }
openbb-regulators = { path = "./extensions/regulators", develop = true }
openbb-mcp-server = { path = "./extensions/mcp_server", optional = true, develop = true, markers = "python_version >= '3.10'" }

# Community dependencies
openbb-alpha-vantage = { path = "./providers/alpha_vantage", optional = true, develop = true }
openbb-biztoc = { path = "./providers/biztoc", optional = true, develop = true }
openbb-cboe = { path = "./providers/cboe", optional = true, develop = true }
openbb-deribit = { path = "./providers/deribit", optional = true, develop = true }
openbb-ecb = { path = "./providers/ecb", optional = true, develop = true }
openbb-famafrench = { path = "./providers/famafrench", optional = true, develop = true }
openbb-finra = { path = "./providers/finra", optional = true, develop = true }
openbb-finviz = { path = "./providers/finviz", optional = true, develop = true }
openbb-multpl = { path = "./providers/multpl", optional = true, develop = true }
openbb-nasdaq = { path = "./providers/nasdaq", optional = true, develop = true }
openbb-seeking-alpha = { path = "./providers/seeking_alpha", optional = true, develop = true }
openbb-stockgrid = { path = "./providers/stockgrid" , optional = true,  develop = true }
openbb-wsj = { path = "./providers/wsj", optional = true, develop = true }

openbb-charting = { path = "./obbject_extensions/charting", optional = true, develop = true }
openbb-econometrics = { path = "./extensions/econometrics", optional = true, develop = true }
openbb-quant-ml = { path = "./extensions/quant_ml", optional = true, develop = true }
openbb-quantitative = { path = "./extensions/quantitative", optional = true, develop = true }
openbb-technical = { path = "./extensions/technical", optional = true, develop = true }
"""


def _ensure_python_module(module_name: str, pip_name: str) -> None:
    """Ensure a Python module is importable, bootstrapping it with pip if needed."""
    if importlib.util.find_spec(module_name) is not None:
        return

    bootstrap_env = os.environ.copy()
    bootstrap_env.setdefault("PYTHONIOENCODING", "utf-8")
    bootstrap_env.setdefault("PYTHONUTF8", "1")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", pip_name],
        check=True,
        env=bootstrap_env,
    )


def _ensure_poetry() -> list[str]:
    """Return the canonical Poetry command after ensuring the module exists."""
    _ensure_python_module("poetry", "poetry")
    return [sys.executable, "-m", "poetry"]


def _restore_original_files(original_files: dict[Path, str]) -> None:
    """Restore files that were temporarily modified during installation."""
    for path, content in original_files.items():
        with open(path, "w", encoding="utf-8", newline="\n") as file:
            file.write(content)


def extract_dependencies(local_dep_path, dev: bool = False):
    """Extract development dependencies from a given package's pyproject.toml."""
    _ensure_python_module("tomlkit", "tomlkit")
    tomlkit = importlib.import_module("tomlkit")
    package_pyproject_path = PLATFORM_PATH / local_dep_path
    if package_pyproject_path.exists():
        with open(package_pyproject_path / "pyproject.toml") as f:
            package_pyproject_toml = tomlkit.load(f)
        if dev:
            return (
                package_pyproject_toml.get("tool", {})
                .get("poetry", {})
                .get("group", {})
                .get("dev", {})
                .get("dependencies", {})
            )
        return (
            package_pyproject_toml.get("tool", {})
            .get("poetry", {})
            .get("dependencies", {})
        )
    return {}


def get_all_dev_dependencies():
    """Aggregate development dependencies from all local packages."""
    _ensure_python_module("tomlkit", "tomlkit")
    tomlkit = importlib.import_module("tomlkit")
    all_dev_dependencies = {}
    local_deps = tomlkit.loads(LOCAL_DEPS).get("tool", {}).get("poetry", {})[
        "dependencies"
    ]
    for _, package_info in local_deps.items():
        if "path" in package_info:
            dev_deps = extract_dependencies(Path(package_info["path"]), dev=True)
            all_dev_dependencies.update(dev_deps)
    return all_dev_dependencies


def install_platform_local(_extras: bool = False):
    """Install the Platform locally for development purposes."""
    _ensure_python_module("tomlkit", "tomlkit")
    tomlkit = importlib.import_module("tomlkit")
    original_files = {
        LOCK: LOCK.read_text(encoding="utf-8"),
        PYPROJECT: PYPROJECT.read_text(encoding="utf-8"),
    }

    local_deps = tomlkit.loads(LOCAL_DEPS).get("tool", {}).get("poetry", {})[
        "dependencies"
    ]
    with open(PYPROJECT) as f:
        pyproject_toml = tomlkit.load(f)
    pyproject_toml.get("tool", {}).get("poetry", {}).get("dependencies", {}).update(
        local_deps
    )

    if _extras:
        dev_dependencies = get_all_dev_dependencies()
        pyproject_toml.get("tool", {}).get("poetry", {}).setdefault(
            "group", {}
        ).setdefault("dev", {}).setdefault("dependencies", {})
        pyproject_toml.get("tool", {}).get("poetry", {})["group"]["dev"][
            "dependencies"
        ].update(dev_dependencies)

    temp_pyproject = tomlkit.dumps(pyproject_toml)

    try:
        with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
            f.write(temp_pyproject)

        poetry_cmd = _ensure_poetry()
        extras_args = ["-E", "all"] if _extras else []
        poetry_env = os.environ.copy()
        poetry_env.setdefault("PYTHONIOENCODING", "utf-8")
        poetry_env.setdefault("PYTHONUTF8", "1")

        subprocess.run(
            poetry_cmd + ["lock", "--regenerate"],
            cwd=PLATFORM_PATH,
            check=True,
            env=poetry_env,
        )
        subprocess.run(
            poetry_cmd + ["install"] + extras_args,
            cwd=PLATFORM_PATH,
            check=True,
            env=poetry_env,
        )

    finally:
        _restore_original_files(original_files)


def install_platform_cli():
    """Install the CLI locally for development purposes."""
    _ensure_python_module("tomlkit", "tomlkit")
    tomlkit = importlib.import_module("tomlkit")
    original_files = {
        CLI_LOCK: CLI_LOCK.read_text(encoding="utf-8"),
        CLI_PYPROJECT: CLI_PYPROJECT.read_text(encoding="utf-8"),
    }

    with open(CLI_PYPROJECT) as f:
        pyproject_toml = tomlkit.load(f)

    # remove "openbb" from dependencies
    pyproject_toml.get("tool", {}).get("poetry", {}).get("dependencies", {}).pop(
        "openbb", None
    )

    temp_pyproject = tomlkit.dumps(pyproject_toml)

    try:
        with open(CLI_PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
            f.write(temp_pyproject)

        poetry_cmd = _ensure_poetry()
        poetry_env = os.environ.copy()
        poetry_env.setdefault("PYTHONIOENCODING", "utf-8")
        poetry_env.setdefault("PYTHONUTF8", "1")

        subprocess.run(
            poetry_cmd + ["lock", "--regenerate"],
            cwd=CLI_PATH,
            check=True,  # noqa: S603
            env=poetry_env,
        )
        subprocess.run(
            poetry_cmd + ["install"],
            cwd=CLI_PATH,
            check=True,
            env=poetry_env,
        )  # noqa: S603

    finally:
        _restore_original_files(original_files)


if __name__ == "__main__":
    args = sys.argv[1:]
    extras = any(arg.lower() in ["-e", "--extras"] for arg in args)
    cli = any(arg.lower() in ["-c", "--cli"] for arg in args)
    try:
        install_platform_local(extras)
        if cli:
            install_platform_cli()
    except (Exception, KeyboardInterrupt) as error:
        print(error, file=sys.stderr)  # noqa: T201
        raise SystemExit(1) from error
