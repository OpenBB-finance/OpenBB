"""Install for development script."""
import subprocess
import sys
from pathlib import Path

import toml

PLATFORM_PATH = Path(__file__).parent.resolve()
LOCK = PLATFORM_PATH / "poetry.lock"
PYPROJECT = PLATFORM_PATH / "pyproject.toml"


LOCAL_DEPS = """
[tool.poetry.dependencies]
python = ">=3.8,<3.12"
openbb-devtools = { path = "./extensions/devtools", develop = true }
openbb-core = { path = "./core", develop = true }

openbb-benzinga = { path = "./providers/benzinga", develop = true }
openbb-fmp = { path = "./providers/fmp", develop = true }
openbb-fred = { path = "./providers/fred", develop = true }
openbb-government-us = { path = "./providers/government_us", develop = true }
openbb-intrinio = { path = "./providers/intrinio", develop = true }
openbb-oecd = { path = "./providers/oecd", develop = true }
openbb-polygon = { path = "./providers/polygon", develop = true }
openbb-sec = { path = "./providers/sec", develop = true }
openbb-tiingo = { path = "./providers/tiingo", develop = true }
openbb-tradingeconomics = { path = "./providers/tradingeconomics", develop = true }

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

# Community dependencies
openbb-alpha-vantage = { path = "./providers/alpha_vantage", optional = true, develop = true }
openbb-biztoc = { path = "./providers/biztoc", optional = true, develop = true }
openbb-cboe = { path = "./providers/cboe", optional = true, develop = true }
openbb-ecb = { path = "./providers/ecb", optional = true, develop = true }
openbb-finra = { path = "./providers/finra", develop = true }
openbb-nasdaq = { path = "./providers/nasdaq", optional = true, develop = true }
openbb-seeking-alpha = { path = "./providers/seeking_alpha", optional = true, develop = true }
openbb-stockgrid = { path = "./providers/stockgrid" ,optional = true,  develop = true }
openbb-wsj = { path = "./providers/wsj", develop = true }
openbb-yfinance = { path = "./providers/yfinance", optional = true, develop = true }

openbb-charting = { path = "./extensions/charting", optional = true, develop = true }
openbb-econometrics = { path = "./extensions/econometrics", optional = true, develop = true }
openbb-quantitative = { path = "./extensions/quantitative", optional = true, develop = true }
openbb-technical = { path = "./extensions/technical", optional = true, develop = true }
"""


def extract_dev_dependencies(local_dep_path):
    """Extract development dependencies from a given package's pyproject.toml."""
    package_pyproject_path = PLATFORM_PATH / local_dep_path
    if package_pyproject_path.exists():
        package_pyproject_toml = toml.load(package_pyproject_path / "pyproject.toml")
        return (
            package_pyproject_toml.get("tool", {})
            .get("poetry", {})
            .get("group", {})
            .get("dev", {})
            .get("dependencies", {})
        )
    return {}


def get_all_dev_dependencies():
    """Aggregate development dependencies from all local packages."""
    all_dev_dependencies = {}
    local_deps = toml.loads(LOCAL_DEPS)["tool"]["poetry"]["dependencies"]
    for _, package_info in local_deps.items():
        if "path" in package_info:
            dev_deps = extract_dev_dependencies(Path(package_info["path"]))
            all_dev_dependencies.update(dev_deps)
    return all_dev_dependencies


def install_local(_extras: bool = False):
    """Install the Platform locally for development purposes."""
    original_lock = LOCK.read_text()
    original_pyproject = PYPROJECT.read_text()

    pyproject_toml = toml.load(PYPROJECT)
    local_deps = toml.loads(LOCAL_DEPS)["tool"]["poetry"]["dependencies"]
    pyproject_toml["tool"]["poetry"]["dependencies"].update(local_deps)

    if _extras:
        dev_dependencies = get_all_dev_dependencies()
        pyproject_toml["tool"]["poetry"].setdefault("group", {}).setdefault(
            "dev", {}
        ).setdefault("dependencies", {})
        pyproject_toml["tool"]["poetry"]["group"]["dev"]["dependencies"].update(
            dev_dependencies
        )

    TEMP_PYPROJECT = toml.dumps(pyproject_toml)

    try:
        with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
            f.write(TEMP_PYPROJECT)

        CMD = [sys.executable, "-m", "poetry"]
        extras_args = ["-E", "all"] if _extras else []

        subprocess.run(
            CMD + ["lock", "--no-update"], cwd=PLATFORM_PATH, check=True  # noqa: S603
        )
        subprocess.run(
            CMD + ["install"] + extras_args, cwd=PLATFORM_PATH, check=True  # noqa: S603
        )

    except (Exception, KeyboardInterrupt) as e:
        print(e)  # noqa: T201
        print("Restoring pyproject.toml and poetry.lock")  # noqa: T201

    finally:
        # Revert pyproject.toml and poetry.lock to their original state
        with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
            f.write(original_pyproject)

        with open(LOCK, "w", encoding="utf-8", newline="\n") as f:
            f.write(original_lock)


if __name__ == "__main__":
    args = sys.argv[1:]
    extras = any(arg.lower() in ["-e", "--extras"] for arg in args)
    install_local(extras)
