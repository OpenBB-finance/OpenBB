"""Keys model"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines

import contextlib
import io
import json
import logging
import os
import sys
from enum import Enum
from typing import Dict, List, Union

import binance
import dotenv
import oandapyV20.endpoints.pricing
import pandas as pd
import praw
import quandl
import requests
import stocksera
from alpha_vantage.timeseries import TimeSeries
from coinmarketcapapi import CoinMarketCapAPI
from oandapyV20 import API as oanda_API
from prawcore.exceptions import ResponseException
from tokenterminal import TokenTerminal

from openbb_terminal import config_terminal as cfg
from openbb_terminal.core.config.paths import USER_ENV_FILE
from openbb_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseApiException,
    CoinbaseProAuth,
    make_coinbase_request,
)
from openbb_terminal.helper_funcs import request
from openbb_terminal.portfolio.brokers.degiro.degiro_model import DegiroModel
from openbb_terminal.rich_config import console
from openbb_terminal.session.hub_model import BASE_URL, patch_user_configs
from openbb_terminal.session.local_model import SESSION_FILE_PATH
from openbb_terminal.session.user import User
from openbb_terminal.terminal_helper import suppress_stdout

logger = logging.getLogger(__name__)

# README PLEASE:
# The API_DICT keys must match the set and check functions format.
#
# This format is used by the KeysController and get_keys_info().
# E.g. tokenterminal -> set_tokenterminal_key & check_tokenterminal_key
#
# Don't forget to add the set function to api.py endpoints dictionary.
# E.g.  "keys.tokenterminal": {"model": "openbb_terminal.keys_model.set_tokenterminal_key"},

API_DICT: Dict = {
    "av": "ALPHA_VANTAGE",
    "fmp": "FINANCIAL_MODELING_PREP",
    "quandl": "QUANDL",
    "polygon": "POLYGON",
    "intrinio": "INTRINIO",
    "databento": "DATABENTO",
    "fred": "FRED",
    "news": "NEWSAPI",
    "tradier": "TRADIER",
    "cmc": "COINMARKETCAP",
    "finnhub": "FINNHUB",
    "reddit": "REDDIT",
    "twitter": "TWITTER",
    "rh": "ROBINHOOD",
    "degiro": "DEGIRO",
    "oanda": "OANDA",
    "openbb": "OPENBB",
    "binance": "BINANCE",
    "bitquery": "BITQUERY",
    "coinbase": "COINBASE",
    "walert": "WHALE_ALERT",
    "glassnode": "GLASSNODE",
    "coinglass": "COINGLASS",
    "cpanic": "CRYPTO_PANIC",
    "ethplorer": "ETHPLORER",
    "smartstake": "SMARTSTAKE",
    "github": "GITHUB",
    "messari": "MESSARI",
    "eodhd": "EODHD",
    "santiment": "SANTIMENT",
    "tokenterminal": "TOKEN_TERMINAL",
    "shroom": "SHROOM",
    "stocksera": "STOCKSERA",
}

# sorting api key section by name
API_DICT = dict(sorted(API_DICT.items()))


class KeyStatus(str, Enum):
    """Class to handle status messages and colors"""

    DEFINED_TEST_FAILED = "defined, test failed"
    NOT_DEFINED = "not defined"
    DEFINED_TEST_PASSED = "defined, test passed"
    DEFINED_TEST_INCONCLUSIVE = "defined, test inconclusive"
    DEFINED_NOT_TESTED = "defined, not tested"

    def __str__(self):
        return self.value

    def colorize(self):
        if self.name == self.DEFINED_TEST_FAILED.name:
            c = "red"
        elif self.name == self.NOT_DEFINED.name:
            c = "grey30"
        elif self.name == self.DEFINED_TEST_PASSED.name:
            c = "green"
        elif self.name == self.DEFINED_TEST_INCONCLUSIVE.name:
            c = "yellow"
        elif self.name == self.DEFINED_NOT_TESTED.name:
            c = "yellow"

        return f"[{c}]{self.value}[/{c}]"


def set_keys(
    keys_dict: Dict[str, Dict[str, Union[str, bool]]],
    persist: bool = False,
    show_output: bool = False,
) -> Dict:
    """Set API keys in bundle.

    Parameters
    ----------
    keys_dict: Dict[str, Dict[str, Union[str, bool]]]
        More info on the required inputs for each API can be found on `keys.get_keys_info()`
    persist: bool
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    Dict
        Status of each key set.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> d = {
            "fred": {"key": "XXXXX"},
            "binance": {"key": "YYYYY", "secret": "ZZZZZ"},
        }
    >>> openbb.keys.set_keys(keys_dict=d)
    """

    status_dict = {}

    for api, kwargs in keys_dict.items():
        expected_args_dict = get_keys_info()

        if api in expected_args_dict:
            received_kwargs_list = list(kwargs.keys())
            expected_kwargs_list = expected_args_dict[api]

            if received_kwargs_list == expected_kwargs_list:
                kwargs["persist"] = persist
                kwargs["show_output"] = show_output
                status_dict[api] = str(
                    getattr(sys.modules[__name__], "set_" + str(api) + "_key")(**kwargs)
                )
            else:
                console.print(
                    f"[red]'{api}' kwargs: {received_kwargs_list} don't match expected: {expected_kwargs_list}.[/red]"
                )
        else:
            console.print(
                f"[red]API '{api}' was not recognized. Please check get_keys_info().[/red]"
            )

    return status_dict


def get_keys_info() -> Dict[str, List[str]]:
    """Get info on available APIs to use in set_keys.

    Returns
    -------
    Dict[str, List[str]]
        Dictionary of expected API keys and arguments
    """
    args_dict = {}

    for api in API_DICT:
        arg_list = list(
            getattr(
                sys.modules[__name__], "set_" + str(api) + "_key"
            ).__code__.co_varnames
        )
        arg_list.remove("persist")
        arg_list.remove("show_output")
        args_dict[api] = arg_list

    return args_dict


def first_time_user() -> bool:
    """Whether a user is a first time user. A first time user is someone with an empty .env file.
    If this is true, it also adds an env variable to make sure this does not run again.

    Returns
    -------
    bool
        Whether or not the user is a first time user
    """
    if USER_ENV_FILE.stat().st_size == 0:
        set_key("OPENBB_PREVIOUS_USE", "True", True)
        return True
    return False


def set_key(env_var_name: str, env_var_value: str, persist: bool = False) -> None:
    """Set API key.

    Parameters
    ----------
    env_var_name: str
        API name
    env_var_value: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    """
    if persist and User.is_guest():
        os.environ[env_var_name] = env_var_value
        dotenv.set_key(str(USER_ENV_FILE), env_var_name, env_var_value)

    # Remove "OPENBB_" prefix from env_var
    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]

    # Set cfg.env_var_name = env_var_value
    setattr(cfg, env_var_name, env_var_value)

    # Send api key to server
    if (
        not User.is_guest()
        and User.is_sync_enabled()
        and env_var_name not in cfg.SENSITIVE_KEYS
        and (env_var_name.startswith("API_") or env_var_name.startswith("OPENBB_"))
    ):
        patch_user_configs(
            key=env_var_name,
            value=env_var_value,
            type_="keys",
            auth_header=User.get_auth_header(),
        )


def get_keys(show: bool = False) -> pd.DataFrame:
    """Get currently set API keys.

    Parameters
    ----------
    show: bool, optional
        Flag to choose whether to show actual keys or not.
        By default, False.

    Returns
    -------
    pd.DataFrame
        Currents keys

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.mykeys()
                       Key
              API
     BITQUERY_KEY  *******
          CMC_KEY  *******
    COINGLASS_KEY  *******
    """

    # TODO: Refactor api variables without prefix API_ and extend API_SOURCE_KEY format

    var_list = [v for v in dir(cfg) if v.startswith("API_") or v.startswith("OPENBB_")]

    current_keys = {}

    for cfg_var_name in var_list:
        cfg_var_value = getattr(cfg, cfg_var_name)
        if cfg_var_value != "REPLACE_ME":
            if cfg_var_name.startswith("OPENBB_"):
                current_keys[cfg_var_name] = cfg_var_value
            else:
                current_keys[cfg_var_name[4:]] = cfg_var_value

    if current_keys:
        df = pd.DataFrame.from_dict(current_keys, orient="index")
        df.index.name = "API"
        df = df.rename(columns={0: "Key"})
        if show:
            return df
        df.loc[:, "Key"] = "*******"
        return df

    return pd.DataFrame()


def set_av_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Alpha Vantage key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.av(key="example_key")
    """

    set_key("OPENBB_API_KEY_ALPHAVANTAGE", key, persist)
    return check_av_key(show_output)


def check_av_key(show_output: bool = False) -> str:
    """Check Alpha Vantage key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME":  # pragma: allowlist secret
        logger.info("Alpha Vantage key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        df = TimeSeries(
            key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
        ).get_intraday(symbol="AAPL")
        if df[0].empty:  # pylint: disable=no-member
            logger.warning("Alpha Vantage key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        else:
            logger.info("Alpha Vantage key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_fmp_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Financial Modeling Prep key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.fmp(key="example_key")
    """

    set_key("OPENBB_API_KEY_FINANCIALMODELINGPREP", key, persist)
    return check_fmp_key(show_output)


def check_fmp_key(show_output: bool = False) -> str:
    """Check Financial Modeling Prep key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    status: str
    """

    if (
        cfg.API_KEY_FINANCIALMODELINGPREP == "REPLACE_ME"  # pragma: allowlist secret
    ):  # pragma: allowlist secret
        logger.info("Financial Modeling Prep key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"
        )
        if r.status_code in [403, 401] or "Error Message" in str(r.content):
            logger.warning("Financial Modeling Prep key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("Financial Modeling Prep key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Financial Modeling Prep key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_quandl_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Quandl key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.quandl(key="example_key")
    """

    set_key("OPENBB_API_KEY_QUANDL", key, persist)
    return check_quandl_key(show_output)


def check_quandl_key(show_output: bool = False) -> str:
    """Check Quandl key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_KEY_QUANDL == "REPLACE_ME":  # pragma: allowlist secret
        logger.info("Quandl key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        try:
            quandl.save_key(cfg.API_KEY_QUANDL)
            quandl.get("EIA/PET_RWTC_D")
            logger.info("Quandl key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        except Exception as _:  # noqa: F841
            logger.warning("Quandl key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_polygon_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Polygon key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.polygon(key="example_key")
    """

    set_key("OPENBB_API_POLYGON_KEY", key, persist)
    return check_polygon_key(show_output)


def check_polygon_key(show_output: bool = False) -> str:
    """Check Polygon key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_POLYGON_KEY == "REPLACE_ME":
        logger.info("Polygon key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17"
            f"?apiKey={cfg.API_POLYGON_KEY}"
        )
        if r.status_code in [403, 401]:
            logger.warning("Polygon key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("Polygon key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Polygon key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_fred_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set FRED key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.fred(key="example_key")
    """

    set_key("OPENBB_API_FRED_KEY", key, persist)
    return check_fred_key(show_output)


def check_fred_key(show_output: bool = False) -> str:
    """Check FRED key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_FRED_KEY == "REPLACE_ME":
        logger.info("FRED key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            f"https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={cfg.API_FRED_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            logger.warning("FRED key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("FRED key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("FRED key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_news_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set News key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.news(key="example_key")
    """

    set_key("OPENBB_API_NEWS_TOKEN", key, persist)
    return check_news_key(show_output)


def check_news_key(show_output: bool = False) -> str:
    """Check News key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_NEWS_TOKEN == "REPLACE_ME":  # nosec
        logger.info("News API key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            f"https://newsapi.org/v2/everything?q=keyword&apiKey={cfg.API_NEWS_TOKEN}"
        )
        if r.status_code in [401, 403]:
            logger.warning("News API key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("News API key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("News API key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_tradier_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Tradier key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.tradier(key="example_key")
    """

    set_key("OPENBB_API_TRADIER_TOKEN", key, persist)
    return check_tradier_key(show_output)


def check_tradier_key(show_output: bool = False) -> str:
    """Check Tradier key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_TRADIER_TOKEN == "REPLACE_ME":  # nosec
        logger.info("Tradier key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            "https://sandbox.tradier.com/v1/markets/quotes",
            params={"symbols": "AAPL"},
            headers={
                "Authorization": f"Bearer {cfg.API_TRADIER_TOKEN}",
                "Accept": "application/json",
            },
        )
        if r.status_code in [401, 403]:
            logger.warning("Tradier key not defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("Tradier key not defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Tradier key not defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_cmc_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Coinmarketcap key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.cmc(key="example_key")
    """

    set_key("OPENBB_API_CMC_KEY", key, persist)
    return check_cmc_key(show_output)


def check_cmc_key(show_output: bool = False) -> str:
    """Check Coinmarketcap key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    status: str
    """

    if cfg.API_CMC_KEY == "REPLACE_ME":
        logger.info("Coinmarketcap key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)

        try:
            cmc.cryptocurrency_map()
            logger.info("Coinmarketcap key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        except Exception:
            logger.info("Coinmarketcap key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_finnhub_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Finnhub key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.finnhub(key="example_key")
    """

    set_key("OPENBB_API_FINNHUB_KEY", key, persist)
    return check_finnhub_key(show_output)


def check_finnhub_key(show_output: bool = False) -> str:
    """Check Finnhub key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_FINNHUB_KEY == "REPLACE_ME":
        logger.info("Finnhub key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = r = request(
            f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg.API_FINNHUB_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            logger.warning("Finnhub key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("Finnhub key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Finnhub key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_reddit_key(
    client_id: str,
    client_secret: str,
    password: str,
    username: str,
    useragent: str,
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Reddit key

    Parameters
    ----------
    client_id: str
        Client ID
    client_secret: str
        Client secret
    password: str
        User password
    username: str
        User username
    useragent: str
        User useragent
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.reddit(
            client_id="example_id",
            client_secret="example_secret",
            password="example_password",
            username="example_username",
            useragent="example_useragent"
        )
    """

    set_key("OPENBB_API_REDDIT_CLIENT_ID", client_id, persist)
    set_key("OPENBB_API_REDDIT_CLIENT_SECRET", client_secret, persist)
    set_key("OPENBB_API_REDDIT_PASSWORD", password, persist)
    set_key("OPENBB_API_REDDIT_USERNAME", username, persist)
    set_key("OPENBB_API_REDDIT_USER_AGENT", useragent, persist)

    return check_reddit_key(show_output)


def check_reddit_key(show_output: bool = False) -> str:
    """Check Reddit key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    reddit_keys = [
        cfg.API_REDDIT_CLIENT_ID,
        cfg.API_REDDIT_CLIENT_SECRET,
        cfg.API_REDDIT_USERNAME,
        cfg.API_REDDIT_PASSWORD,
        cfg.API_REDDIT_USER_AGENT,
    ]
    if "REPLACE_ME" in reddit_keys:
        logger.info("Reddit key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        try:
            with suppress_stdout():
                praw_api = praw.Reddit(
                    client_id=cfg.API_REDDIT_CLIENT_ID,
                    client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                    username=cfg.API_REDDIT_USERNAME,
                    user_agent=cfg.API_REDDIT_USER_AGENT,
                    password=cfg.API_REDDIT_PASSWORD,
                    check_for_updates=False,
                    comment_kind="t1",
                    message_kind="t4",
                    redditor_kind="t2",
                    submission_kind="t3",
                    subreddit_kind="t5",
                    trophy_kind="t6",
                    oauth_url="https://oauth.reddit.com",
                    reddit_url="https://www.reddit.com",
                    short_url="https://redd.it",
                    ratelimit_seconds=5,
                    timeout=16,
                )

                praw_api.user.me()
            logger.info("Reddit key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        except (Exception, ResponseException):
            logger.warning("Reddit key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_bitquery_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Bitquery key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.bitquery(key="example_key")
    """

    set_key("OPENBB_API_BITQUERY_KEY", key, persist)
    return check_bitquery_key(show_output)


def check_bitquery_key(show_output: bool = False) -> str:
    """Check Bitquery key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    bitquery = cfg.API_BITQUERY_KEY
    if "REPLACE_ME" in bitquery:
        logger.info("Bitquery key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        headers = {"x-api-key": cfg.API_BITQUERY_KEY}
        query = """
        {
        ethereum {
        dexTrades(options: {limit: 10, desc: "count"}) {
            count
            protocol
        }}}
        """
        r = request(
            "https://graphql.bitquery.io",
            method="POST",
            json={"query": query},
            headers=headers,
        )
        if r.status_code == 200:
            logger.info("Bitquery key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Bitquery key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_twitter_key(
    access_token: str,
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Twitter key

    Parameters
    ----------
    key: str
        API key
    secret: str
        API secret
    access_token: str
        API token
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.twitter(
            key="example_key",
            secret="example_secret",
            access_token="example_access_token"
        )
    """

    set_key("OPENBB_API_TWITTER_BEARER_TOKEN", access_token, persist)

    return check_twitter_key(show_output)


def check_twitter_key(show_output: bool = False) -> str:
    """Check Twitter key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_TWITTER_BEARER_TOKEN == "REPLACE_ME":
        logger.info("Twitter key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        params = {
            "query": "(\\$AAPL) (lang:en)",
            "max_results": "10",
            "tweet.fields": "created_at,lang",
        }
        r = request(
            "https://api.twitter.com/2/tweets/search/recent",
            params=params,  # type: ignore
            headers={"authorization": "Bearer " + cfg.API_TWITTER_BEARER_TOKEN},
        )
        if r.status_code == 200:
            logger.info("Twitter key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        elif r.status_code in [401, 403]:
            logger.warning("Twitter key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        else:
            logger.warning("Twitter key defined, test failed")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_rh_key(
    username: str,
    password: str,
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Robinhood key

    Parameters
    ----------
    username: str
        User username
    password: str
        User password
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.rh(
            username="example_username",
            password="example_password"
        )
    """

    set_key("OPENBB_RH_USERNAME", username, persist)
    set_key("OPENBB_RH_PASSWORD", password, persist)

    return check_rh_key(show_output)


def check_rh_key(show_output: bool = False) -> str:
    """Check Robinhood key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    rh_keys = [cfg.RH_USERNAME, cfg.RH_PASSWORD]
    if "REPLACE_ME" in rh_keys:
        logger.info("Robinhood key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        logger.info("Robinhood key defined, not tested")
        status = KeyStatus.DEFINED_NOT_TESTED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_degiro_key(
    username: str,
    password: str,
    secret: str = "",
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Degiro key

    Parameters
    ----------
    username: str
        User username
    password: str
        User password
    secret: str, optional
        User secret
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.degiro(
            username="example_username",
            password="example_password"
        )
    """

    set_key("OPENBB_DG_USERNAME", username, persist)
    set_key("OPENBB_DG_PASSWORD", password, persist)
    set_key("OPENBB_DG_TOTP_SECRET", secret, persist)

    return check_degiro_key(show_output)


def check_degiro_key(show_output: bool = False) -> str:
    """Check Degiro key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    dg_keys = [cfg.DG_USERNAME, cfg.DG_PASSWORD, cfg.DG_TOTP_SECRET]
    if "REPLACE_ME" in dg_keys:
        logger.info("Degiro key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        dg = DegiroModel()
        try:
            f = io.StringIO()  # suppress stdout
            with contextlib.redirect_stdout(f):
                check_creds = dg.check_credentials()  # pylint: disable=no-member

            if "2FA is enabled" in f.getvalue() or check_creds:
                logger.info("Degiro key defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
            else:
                raise Exception

            logger.info("Degiro key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED

        except Exception:
            logger.info("Degiro key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

        del dg  # ensure the object is destroyed explicitly

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_oanda_key(
    account: str,
    access_token: str,
    account_type: str = "",
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Oanda key

    Parameters
    ----------
    account: str
        User account
    access_token: str
        User token
    account_type: str, optional
        User account type
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.oanda(
            account="example_account",
            access_token="example_access_token",
            account_type="example_account_type"
        )
    """

    set_key("OPENBB_OANDA_ACCOUNT", account, persist)
    set_key("OPENBB_OANDA_TOKEN", access_token, persist)
    set_key("OPENBB_OANDA_ACCOUNT_TYPE", account_type, persist)

    return check_oanda_key(show_output)


def check_oanda_key(show_output: bool = False) -> str:
    """Check Oanda key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    oanda_keys = [cfg.OANDA_TOKEN, cfg.OANDA_ACCOUNT]
    if "REPLACE_ME" in oanda_keys:
        logger.info("Oanda key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        client = oanda_API(access_token=cfg.OANDA_TOKEN)
        account = cfg.OANDA_ACCOUNT
        try:
            parameters = {"instruments": "EUR_USD"}
            request_ = oandapyV20.endpoints.pricing.PricingInfo(
                accountID=account, params=parameters
            )
            client.request(request_)
            logger.info("Oanda key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED

        except Exception:
            logger.info("Oanda key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_binance_key(
    key: str,
    secret: str,
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Binance key

    Parameters
    ----------
    key: str
        API key
    secret: str
        API secret
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.binance(
            key="example_key",
            secret="example_secret"
        )
    """

    set_key("OPENBB_API_BINANCE_KEY", key, persist)
    set_key("OPENBB_API_BINANCE_SECRET", secret, persist)

    return check_binance_key(show_output)


def check_binance_key(show_output: bool = False) -> str:
    """Check Binance key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if "REPLACE_ME" in [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]:
        logger.info("Binance key not defined")
        status = KeyStatus.NOT_DEFINED

    else:
        try:
            client = binance.Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
            client.get_account_api_permissions()
            logger.info("Binance key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        except Exception:
            logger.warning("Binance key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_coinbase_key(
    key: str,
    secret: str,
    passphrase: str,
    persist: bool = False,
    show_output: bool = False,
) -> str:
    """Set Coinbase key

    Parameters
    ----------
    key: str
        API key
    secret: str
        API secret
    passphrase: str
        Account passphrase
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.coinbase(
            key="example_key",
            secret="example_secret",
            passphrase="example_passphrase"
        )
    """

    set_key("OPENBB_API_COINBASE_KEY", key, persist)
    set_key("OPENBB_API_COINBASE_SECRET", secret, persist)
    set_key("OPENBB_API_COINBASE_PASS_PHRASE", passphrase, persist)

    return check_coinbase_key(show_output)


def check_coinbase_key(show_output: bool = False) -> str:
    """Check Coinbase key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    status: str
    """

    if "REPLACE_ME" in [
        cfg.API_COINBASE_KEY,
        cfg.API_COINBASE_SECRET,
        cfg.API_COINBASE_PASS_PHRASE,
    ]:
        logger.info("Coinbase key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        auth = CoinbaseProAuth(
            cfg.API_COINBASE_KEY,
            cfg.API_COINBASE_SECRET,
            cfg.API_COINBASE_PASS_PHRASE,
        )
        try:
            resp = make_coinbase_request("/accounts", auth=auth)
        except CoinbaseApiException:
            resp = None
        if not resp:
            logger.warning("Coinbase key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        else:
            logger.info("Coinbase key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_walert_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Walert key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.walert(key="example_key")
    """

    set_key("OPENBB_API_WHALE_ALERT_KEY", key, persist)
    return check_walert_key(show_output)


def check_walert_key(show_output: bool = False) -> str:
    """Check Walert key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_WHALE_ALERT_KEY == "REPLACE_ME":
        logger.info("Walert key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        url = (
            "https://api.whale-alert.io/v1/transactions?api_key="
            + cfg.API_WHALE_ALERT_KEY
        )
        try:
            response = request(url)
            if not 200 <= response.status_code < 300:
                logger.warning("Walert key defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
            else:
                logger.info("Walert key defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
        except Exception:
            logger.info("Walert key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_glassnode_key(
    key: str, persist: bool = False, show_output: bool = False
) -> str:
    """Set Glassnode key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.glassnode(key="example_key")
    """

    set_key("OPENBB_API_GLASSNODE_KEY", key, persist)
    return check_glassnode_key(show_output)


def check_glassnode_key(show_output: bool = False) -> str:
    """Check Glassnode key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_GLASSNODE_KEY == "REPLACE_ME":
        logger.info("Glassnode key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        url = "https://api.glassnode.com/v1/metrics/market/price_usd_close"

        parameters = {
            "api_key": cfg.API_GLASSNODE_KEY,
            "a": "BTC",
            "i": "24h",
            "s": str(1_614_556_800),
            "u": str(1_641_227_783_561),
        }

        r = request(url, params=parameters)
        if r.status_code == 200:
            logger.info("Glassnode key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Glassnode key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_coinglass_key(
    key: str, persist: bool = False, show_output: bool = False
) -> str:
    """Set Coinglass key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.coinglass(key="example_key")
    """

    set_key("OPENBB_API_COINGLASS_KEY", key, persist)
    return check_coinglass_key(show_output)


def check_coinglass_key(show_output: bool = False) -> str:
    """Check Coinglass key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_COINGLASS_KEY == "REPLACE_ME":
        logger.info("Coinglass key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        url = "https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?&symbol=BTC&interval=0"

        headers = {"coinglassSecret": cfg.API_COINGLASS_KEY}

        response = request(url, headers=headers)

        if """success":false""" in str(response.content):
            logger.warning("Coinglass key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif response.status_code == 200:
            logger.info("Coinglass key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Coinglass key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_cpanic_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Cpanic key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.cpanic(key="example_key")
    """

    set_key("OPENBB_API_CRYPTO_PANIC_KEY", key, persist)
    return check_cpanic_key(show_output)


def check_cpanic_key(show_output: bool = False) -> str:
    """Check Cpanic key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_CRYPTO_PANIC_KEY == "REPLACE_ME":
        logger.info("cpanic key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        crypto_panic_url = f"https://cryptopanic.com/api/v1/posts/?auth_token={cfg.API_CRYPTO_PANIC_KEY}"
        response = request(crypto_panic_url)

        if response.status_code == 200:
            logger.info("Cpanic key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Cpanic key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_ethplorer_key(
    key: str, persist: bool = False, show_output: bool = False
) -> str:
    """Set Ethplorer key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.ethplorer(key="example_key")
    """

    set_key("OPENBB_API_ETHPLORER_KEY", key, persist)
    return check_ethplorer_key(show_output)


def check_ethplorer_key(show_output: bool = False) -> str:
    """Check Ethplorer key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_ETHPLORER_KEY == "REPLACE_ME":
        logger.info("ethplorer key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        ethplorer_url = "https://api.ethplorer.io/getTokenInfo/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984?apiKey="
        ethplorer_url += cfg.API_ETHPLORER_KEY

        try:
            response = request(ethplorer_url)
            if response.status_code == 200:
                logger.info("ethplorer key defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
            else:
                logger.warning("ethplorer key defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
        except Exception as _:  # noqa: F841
            logger.info("ethplorer key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_smartstake_key(
    key: str, access_token: str, persist: bool = False, show_output: bool = False
):
    """Set Smartstake key.

    Parameters
    ----------
    key: str
        API key
    access_token: str
        API token
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.smartstake(
            key="example_key",
            access_token="example_access_token",
            )
    """

    set_key("OPENBB_API_SMARTSTAKE_KEY", key, persist)
    set_key("OPENBB_API_SMARTSTAKE_TOKEN", access_token, persist)
    return check_smartstake_key(show_output)


def check_smartstake_key(show_output: bool = False) -> str:
    """Check Smartstake key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if "REPLACE_ME" in [
        cfg.API_SMARTSTAKE_TOKEN,
        cfg.API_SMARTSTAKE_KEY,
    ]:
        status = KeyStatus.NOT_DEFINED
    else:
        payload = {
            "type": "history",
            "dayCount": 30,
            "key": cfg.API_SMARTSTAKE_KEY,
            "token": cfg.API_SMARTSTAKE_TOKEN,
        }

        smartstake_url = "https://prod.smartstakeapi.com/listData?app=TERRA"
        response = request(smartstake_url, params=payload)  # type: ignore

        try:
            if (
                "errors" in str(response.content)
                or response.status_code < 200
                or response.status_code >= 300
            ):
                logger.warning("Smartstake key defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
            elif 200 <= response.status_code < 300:
                logger.info("Smartstake key defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
            else:
                logger.warning("Smartstake key defined, test inconclusive")
                status = KeyStatus.DEFINED_TEST_INCONCLUSIVE
        except Exception as _:  # noqa: F841
            logger.warning("Smartstake key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_github_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set GitHub key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.github(key="example_key")
    """

    set_key("OPENBB_API_GITHUB_KEY", key, persist)
    return check_github_key(show_output)


def check_github_key(show_output: bool = False) -> str:
    """Check GitHub key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_GITHUB_KEY == "REPLACE_ME":  # pragma: allowlist secret
        logger.info("GitHub key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        status = KeyStatus.DEFINED_NOT_TESTED
        # github api will not fail for the first requests without key
        # only after certain amount of requests the user will get rate limited

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_messari_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Messari key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.messari(key="example_key")
    """

    set_key("OPENBB_API_MESSARI_KEY", key, persist)
    return check_messari_key(show_output)


def check_messari_key(show_output: bool = False) -> str:
    """Check Messari key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if (
        cfg.API_MESSARI_KEY == "REPLACE_ME"  # pragma: allowlist secret
    ):  # pragma: allowlist secret
        logger.info("Messari key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        url = "https://data.messari.io/api/v2/assets/bitcoin/profile"
        headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}
        params = {"fields": "profile/general/overview/official_links"}
        r = request(url, headers=headers, params=params)

        if r.status_code == 200:
            logger.info("Messari key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Messari key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_eodhd_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Eodhd key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.eodhd(key="example_key")
    """

    set_key("OPENBB_API_EODHD_KEY", key, persist)
    return check_eodhd_key(show_output)


def check_eodhd_key(show_output: bool = False) -> str:
    """Check Eodhd key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_EODHD_KEY == "REPLACE_ME":  # nosec
        logger.info("End of Day Historical Data key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        request_url = f"https://eodhistoricaldata.com/api/exchanges-list/?api_token={cfg.API_EODHD_KEY}&fmt=json"
        r = request(request_url)
        if r.status_code == 200:
            logger.info("Eodhd key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Eodhd key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_santiment_key(
    key: str, persist: bool = False, show_output: bool = False
) -> str:
    """Set Santiment key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.santiment(key="example_key")
    """

    set_key("OPENBB_API_SANTIMENT_KEY", key, persist)
    return check_santiment_key(show_output)


def check_santiment_key(show_output: bool = False) -> str:
    """Check Santiment key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_SANTIMENT_KEY == "REPLACE_ME":
        logger.info("santiment key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        headers = {
            "Content-Type": "application/graphql",
            "Authorization": f"Apikey {cfg.API_SANTIMENT_KEY}",
        }

        # pylint: disable=line-too-long
        data = '\n{{ getMetric(metric: "dev_activity"){{ timeseriesData( slug: "ethereum" from: ""2020-02-10T07:00:00Z"" to: "2020-03-10T07:00:00Z" interval: "1w"){{ datetime value }} }} }}'  # noqa: E501

        response = request(
            "https://api.santiment.net/graphql",
            method="POST",
            headers=headers,
            data=data,
        )
        try:
            if response.status_code == 200:
                logger.info("santiment key defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
            else:
                logger.warning("santiment key defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
        except Exception as _:  # noqa: F841
            logger.info("santiment key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_shroom_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Shroom key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.shroom(key="example_key")
    """

    set_key("OPENBB_API_SHROOM_KEY", key, persist)
    return check_shroom_key(show_output)


def check_shroom_key(show_output: bool = False) -> str:
    """Check Shroom key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_SHROOM_KEY == "REPLACE_ME":
        logger.info("Shroom key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        try:
            response = request(
                "https://node-api.flipsidecrypto.com/queries",
                method="POST",
                headers={"x-api-key": cfg.API_SHROOM_KEY},
            )
            if response.status_code == 400:
                # this is expected because shroom returns 400 when query is not passed
                logger.info("Shroom key defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
            elif response.status_code == 401:
                logger.warning("Shroom key defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
            else:
                logger.warning("Shroom key defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
        except requests.exceptions.RequestException:
            logger.warning("Shroom key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
    if show_output:
        console.print(status.colorize())

    return str(status)


def set_tokenterminal_key(
    key: str, persist: bool = False, show_output: bool = False
) -> str:
    """Set Token Terminal key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.tokenterminal(key="example_key")
    """
    set_key("OPENBB_API_TOKEN_TERMINAL_KEY", key, persist)
    return check_tokenterminal_key(show_output)


def check_tokenterminal_key(show_output: bool = False) -> str:
    """Check Token Terminal key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """
    if cfg.API_TOKEN_TERMINAL_KEY == "REPLACE_ME":
        logger.info("Token Terminal key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        token_terminal = TokenTerminal(key=cfg.API_TOKEN_TERMINAL_KEY)

        if "message" in token_terminal.get_all_projects():
            logger.warning("Token Terminal key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        else:
            logger.info("Token Terminal key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_stocksera_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Stocksera key.

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.stocksera(key="example_key")
    """
    set_key("OPENBB_API_STOCKSERA_KEY", key, persist)
    return check_stocksera_key(show_output)


def check_stocksera_key(show_output: bool = False):
    """Check Stocksera key

    Parameters
    ----------
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """
    if cfg.API_STOCKSERA_KEY == "REPLACE_ME":
        logger.info("Stocksera key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        client = stocksera.Client(api_key=cfg.API_STOCKSERA_KEY)

        try:
            client.borrowed_shares(ticker="AAPL")
            logger.info("Stocksera key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        except Exception as _:  # noqa: F841
            logger.warning("Stocksera key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())
    return str(status)


def set_openbb_personal_access_token(
    key: str, persist: bool = False, show_output: bool = False
):
    """Set OpenBB Personal Access Token.

    Parameters
    ----------
    key: str
        Personal Access Token
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.openbb(key="example_key")
    """
    set_key("OPENBB_OPENBB_PERSONAL_ACCESS_TOKEN", key, persist)
    return check_openbb_personal_access_token(show_output)


def check_openbb_personal_access_token(show_output: bool = False):
    """Check OpenBB Personal Access Token

    Returns
    -------
    str
        Status of key set
    """
    if cfg.OPENBB_PERSONAL_ACCESS_TOKEN == "REPLACE_ME":
        logger.info("OpenBB Personal Access Token not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        try:
            access_token = ""

            # TODO: is there a better way to test the key?
            # This requires a valid session file

            if os.path.isfile(SESSION_FILE_PATH):
                with open(SESSION_FILE_PATH) as f:
                    access_token = json.load(f).get("access_token")

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            response = request(
                url=f"{BASE_URL}sdk/token", method="GET", headers=headers
            )

            token = response.json().get("token")

            if (
                response.status_code == 200
                and token == cfg.OPENBB_PERSONAL_ACCESS_TOKEN
            ):
                logger.info("OpenBB Personal Access Token defined, test passed")
                status = KeyStatus.DEFINED_TEST_PASSED
            else:
                logger.warning("OpenBB Personal Access Token. defined, test failed")
                status = KeyStatus.DEFINED_TEST_FAILED
        except requests.exceptions.RequestException:
            logger.warning("OpenBB Personal Access Token. defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize())
    return str(status)


def set_intrinio_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set Intrinio key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.intrinio(key="example_key")
    """

    set_key("OPENBB_API_INTRINIO_KEY", key, persist)
    return check_intrinio_key(show_output)


def check_intrinio_key(show_output: bool = False) -> str:
    """Check Intrinio key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_INTRINIO_KEY == "REPLACE_ME":
        logger.info("Intrinio key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            f"https://api-v2.intrinio.com/securities/AAPL/prices?api_key={cfg.API_INTRINIO_KEY}"
        )
        if r.status_code in [403, 401, 429]:
            logger.warning("Intrinio key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("Intrinio key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Intrinio key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)


def set_databento_key(
    key: str, persist: bool = False, show_output: bool = False
) -> str:
    """Set DataBento key

    Parameters
    ----------
    key: str
        API key
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.databento(key="example_key")
    """

    set_key("OPENBB_API_DATABENTO_KEY", key, persist)
    return check_databento_key(show_output)


def check_databento_key(show_output: bool = False) -> str:
    """Check DataBento key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    if cfg.API_DATABENTO_KEY == "REPLACE_ME":
        logger.info("DataBento key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            "https://hist.databento.com/v0/metadata.list_datasets",
            auth=(f"{cfg.API_DATABENTO_KEY}", ""),
        )
        if r.status_code in [403, 401, 429]:
            logger.warning("DataBento key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("DataBento key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("DataBento key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)
