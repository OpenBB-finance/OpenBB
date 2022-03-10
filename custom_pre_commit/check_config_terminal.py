""" Check config_terminal.py """
__docformat__ = "numpy"

import sys
import os
from typing import List

# pylint: disable=W0105

"""
Disables this for a better solution. Here is the code to add in custom pre-commit items
  - repo: local
    hooks:
      - id: check-config
        name: check-config
        entry: python custom_pre_commit/check_config_terminal.py
        language: python
        language_version: python3
        types: ["file"]
        pass_filenames: false
"""

# This is a dictionary of all settings to check in config_terminal.py
settings = {
    "DEBUG_MODE": "DEBUG_MODE = False",
    "PAPERMILL_NOTEBOOK_REPORT_PORT": 'PAPERMILL_NOTEBOOK_REPORT_PORT = "8888"',
    "LOGGING_VERBOSITY": "LOGGING_VERBOSITY = 0",
    "LOGGING_HANDLERS": 'LOGGING_HANDLERS = os.getenv("GT_LOGGING_HANDLERS") or "file"',
    "LOGGING_ID": 'LOGGING_ID = os.getenv("GT_LOGGING_ID") or None',
    "LOGGING_FILE": 'LOGGING_FILE = ""',
    "LOGGING_VERSION": 'LOGGING_VERSION = os.getenv("GT_LOGGING_VERSION") or "ver:1.0.0"',
    "API_KEY_ALPHAVANTAGE": 'API_KEY_ALPHAVANTAGE = os.getenv("GT_API_KEY_ALPHAVANTAGE") or "REPLACE_ME"',
    "API_KEY_QUANDL": 'API_KEY_QUANDL = os.getenv("GT_API_KEY_QUANDL") or "REPLACE_ME"',
    "API_REDDIT_CLIENT_ID": 'API_REDDIT_CLIENT_ID = os.getenv("GT_API_REDDIT_CLIENT_ID") or "REPLACE_ME"',
    "API_REDDIT_CLIENT_SECRET": 'API_REDDIT_CLIENT_SECRET = os.getenv("GT_API_REDDIT_CLIENT_SECRET") or "REPLACE_ME"',
    "API_REDDIT_USERNAME": 'API_REDDIT_USERNAME = os.getenv("GT_API_REDDIT_USERNAME") or "REPLACE_ME"',
    "API_REDDIT_USER_AGENT": 'API_REDDIT_USER_AGENT = os.getenv("GT_API_REDDIT_USER_AGENT") or "REPLACE_ME"',
    "API_REDDIT_PASSWORD": 'API_REDDIT_PASSWORD = os.getenv("GT_API_REDDIT_PASSWORD") or "REPLACE_ME"',
    "API_POLYGON_KEY": 'API_POLYGON_KEY = os.getenv("GT_API_POLYGON_KEY") or "REPLACE_ME"',
    "API_TWITTER_KEY ": 'API_TWITTER_KEY = os.getenv("GT_API_TWITTER_KEY") or "REPLACE_ME"',
    "API_TWITTER_SECRET_KEY": 'API_TWITTER_SECRET_KEY = os.getenv("GT_API_TWITTER_SECRET_KEY") or "REPLACE_ME"',
    "API_TWITTER_BEARER_TOKEN": 'API_TWITTER_BEARER_TOKEN = os.getenv("GT_API_TWITTER_BEARER_TOKEN") or "REPLACE_ME"',
    "API_FRED_KEY": 'API_FRED_KEY = os.getenv("GT_API_FRED_KEY") or "REPLACE_ME"',
    "API_NEWS_TOKEN": 'API_NEWS_TOKEN = os.getenv("GT_API_NEWS_TOKEN") or "REPLACE_ME"',
    "RH_USERNAME": 'RH_USERNAME = os.getenv("GT_RH_USERNAME") or "REPLACE_ME"',
    "RH_PASSWORD": 'RH_PASSWORD = os.getenv("GT_RH_PASSWORD") or "REPLACE_ME"',
    "DG_USERNAME": 'DG_USERNAME = os.getenv("GT_DG_USERNAME") or "REPLACE_ME"',
    "DG_PASSWORD": 'DG_PASSWORD = os.getenv("GT_DG_PASSWORD") or "REPLACE_ME"',
    "DG_TOTP_SECRET": 'DG_TOTP_SECRET = os.getenv("GT_DG_TOTP_SECRET") or None',
    "OANDA_ACCOUNT_TYPE": 'OANDA_ACCOUNT_TYPE = os.getenv("GT_OANDA_ACCOUNT_TYPE") or "practice"',
    "OANDA_ACCOUNT": 'OANDA_ACCOUNT = os.getenv("GT_OANDA_ACCOUNT") or "REPLACE_ME"',
    "OANDA_TOKEN": 'OANDA_TOKEN = os.getenv("GT_OANDA_TOKEN") or "REPLACE_ME"',
    "TRADIER_TOKEN": 'TRADIER_TOKEN = os.getenv("GT_API_TRADIER_TOKEN") or "REPLACE_ME"',
    "WEBDRIVER_TO_USE": 'WEBDRIVER_TO_USE = "chrome"',
    "PATH_TO_SELENIUM_DRIVER": 'PATH_TO_SELENIUM_DRIVER = None  # Replace with "PATH"',
    "API_CMC_KEY": 'API_CMC_KEY = os.getenv("GT_API_CMC_KEY") or "REPLACE_ME"',
    "API_BINANCE_KEY": 'API_BINANCE_KEY = os.getenv("GT_API_BINANCE_KEY") or "REPLACE_ME"',
    "API_BINANCE_SECRET": 'API_BINANCE_SECRET = os.getenv("GT_API_BINANCE_SECRET") or "REPLACE_ME"',
    "API_FINNHUB_KEY": 'API_FINNHUB_KEY = os.getenv("GT_API_FINNHUB_KEY") or "REPLACE_ME"',
    "API_IEX_TOKEN": 'API_IEX_TOKEN = os.getenv("GT_API_IEX_KEY") or "REPLACE_ME"',
    "API_SENTIMENTINVESTOR_TOKEN": 'API_SENTIMENTINVESTOR_TOKEN = os.getenv("GT_API_SENTIMENTINVESTOR_TOKEN") or "REPLACE_ME"',  # noqa
    "API_COINBASE_KEY": 'API_COINBASE_KEY = os.getenv("GT_API_COINBASE_KEY") or "REPLACE_ME"',
    "API_COINBASE_SECRET": 'API_COINBASE_SECRET = os.getenv("GT_API_COINBASE_SECRET") or "REPLACE_ME"',
    "API_COINBASE_PASS_PHRASE": 'API_COINBASE_PASS_PHRASE = os.getenv("GT_API_COINBASE_PASS_PHRASE") or "REPLACE_ME"',
    "API_WHALE_ALERT_KEY": 'API_WHALE_ALERT_KEY = os.getenv("GT_API_WHALE_ALERT_KEY") or "REPLACE_ME"',
    "API_GLASSNODE_KEY": 'API_GLASSNODE_KEY = os.getenv("GT_API_GLASSNODE_KEY") or "REPLACE_ME"',
    "API_COINGLASS_KEY": 'API_COINGLASS_KEY = os.getenv("GT_API_COINGLASS_KEY") or "REPLACE_ME"',
    "API_ETHPLORER_KEY": 'API_ETHPLORER_KEY = os.getenv("GT_API_ETHPLORER_KEY") or "freekey"',
    "API_CRYPTO_PANIC_KEY": 'API_CRYPTO_PANIC_KEY = os.getenv("GT_API_CRYPTO_PANIC_KEY") or "REPLACE_ME"',
    "API_BITQUERY_KEY": 'API_BITQUERY_KEY = os.getenv("GT_API_BITQUERY_KEY") or "REPLACE_ME"',
}


def search(lst: List[str], search_item: str):
    """
    Searches a list for an item

    Parameters
    ----------
    lst : List[str]
        The list of strings to search
    search_item : str
        The item to search for in the strings

    """
    for i, val in enumerate(lst):
        if search_item + " " in val:
            return i, val
    return None, None


def check_setting(lines: List[str], setting: str, value: str) -> bool:
    """
    Checks the setting, replaces if not compliant

    Parameters
    ----------
    lines : List[str]
        The list of strings to search
    setting : str
        The setting to check
    value : str
        The correct value of the setting

    Returns
    ----------
    correct : bool
        Returns whether the setting was already correct
    """
    debug_line, debug_val = search(lines, setting)

    if debug_val == value:
        return True

    lines[debug_line] = value
    return False


def main():
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, "gamestonk_terminal", "config_terminal.py")
    with open(path) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    returns = [check_setting(lines, k, v) for k, v in settings.items()]

    if False not in returns:
        print("Success")
        sys.exit(0)

    with open(path, "w") as file:
        for element in lines:
            file.write(element + "\n")

    sys.exit(1)


if __name__ == "__main__":
    main()
