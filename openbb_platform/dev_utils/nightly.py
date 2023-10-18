import toml
import sys
import subprocess
from pathlib import Path

# from openbb_platform.dev_install import (
#     PLATFORM_PATH,
#     PYPROJECT,
#     LOCAL_DEPS,
# )


PLATFORM_PATH = Path(__file__).parent.parent.resolve()
PYPROJECT = PLATFORM_PATH / "pyproject.toml"


LOCAL_DEPS = """
[tool.poetry.dependencies]
python = ">=3.8,<3.12"
openbb-provider = { path = "./platform/provider", develop = true }
openbb-core = { path = "./platform/core", develop = true }

openbb-benzinga = { path = "./providers/benzinga", develop = true }
openbb-fmp = { path = "./providers/fmp", develop = true }
openbb-fred = { path = "./providers/fred", develop = true }
openbb-intrinio = { path = "./providers/intrinio", develop = true }
openbb-polygon = { path = "./providers/polygon", develop = true }
openbb-tradingeconomics = { path = "./providers/tradingeconomics", develop = true }
openbb-oecd = { path = "./providers/oecd", develop = true }

openbb-crypto = { path = "./extensions/crypto", develop = true }
openbb-economy = { path = "./extensions/economy", develop = true }
openbb-forex = { path = "./extensions/forex", develop = true }
openbb-fixedincome = { path = "./extensions/fixedincome", develop = true }
openbb-news = { path = "./extensions/news", develop = true }
openbb-stocks = { path = "./extensions/stocks", develop = true }

# Community dependencies
openbb-alpha-vantage = { path = "./providers/alpha_vantage", optional = true, develop = true }
openbb-cboe = { path = "./providers/cboe", optional = true, develop = true }
openbb-quandl = { path = "./providers/quandl", optional = true, develop = true }
openbb-yfinance = { path = "./providers/yfinance", optional = true, develop = true }

openbb-charting = { path = "./extensions/charting", optional = true, develop = true }
openbb-futures = { path = "./extensions/futures", optional = true, develop = true }
openbb-qa = { path = "./extensions/qa", optional = true, develop = true }
openbb-ta = { path = "./extensions/ta", optional = true, develop = true }
openbb-econometrics = { path = "./extensions/econometrics", optional = true, develop = true }
"""


def build():
    """Build the Platform package."""

    original_pyproject = PYPROJECT.read_text()

    pyproject_toml = toml.load(PYPROJECT)
    pyproject_toml["tool"]["poetry"]["dependencies"] = toml.loads(LOCAL_DEPS)["tool"][
        "poetry"
    ]["dependencies"]

    temp_pyproject = toml.dumps(pyproject_toml)

    PYPROJECT.write_text(temp_pyproject)

    CMD = [sys.executable, "-m", "poetry"]

    subprocess.run(  # noqa: PLW1510
        CMD + ["build"], cwd=PLATFORM_PATH, check=True  # noqa: S603
    )

    # we restore the original pyproject.toml
    with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
        f.write(original_pyproject)


if __name__ == "__main__":
    build()
