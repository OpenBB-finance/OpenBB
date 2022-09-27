import logging
import os
from typing import Dict
import binance
import dotenv
import quandl
import requests
from prawcore.exceptions import ResponseException
import praw
import pyEX
from pyEX.common.exception import PyEXception
import oandapyV20.endpoints.pricing
from oandapyV20 import API as oanda_API
from oandapyV20.exceptions import V20Error
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from alpha_vantage.timeseries import TimeSeries
from openbb_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseProAuth,
    make_coinbase_request,
    CoinbaseApiException,
)
from openbb_terminal import config_terminal as cfg
from openbb_terminal.core.config.paths import USER_ENV_FILE
from openbb_terminal.rich_config import console

from openbb_terminal.terminal_helper import suppress_stdout
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


def set_key(env_var_name: str, env_var_value: str, persist: bool = False) -> None:
    """Set API key.

    Parameters
    ----------
        env_var_name: str
            API name
        env_var_value: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.
    """
    if persist:
        os.environ[env_var_name] = env_var_value
        dotenv.set_key(str(USER_ENV_FILE), env_var_name, env_var_value)

    # Remove "OPENBB_" prefix from env_var
    if env_var_name.startswith("OPENBB_"):
        env_var_name = env_var_name[7:]

    # Set cfg.env_var_name = env_var_value
    setattr(cfg, env_var_name, env_var_value)


def get_keys() -> Dict:
    """Get dictionary with currently set API keys.

    Returns:
        Dict: key: API -> values: KEY.
    """

    # TODO: Refactor api variables without prefix API_

    var_list = [v for v in dir(cfg) if v.startswith("API_")]

    current_keys = {}

    for cfg_var_name in var_list:
        cfg_var_value = getattr(cfg, cfg_var_name)
        current_keys[cfg_var_name] = cfg_var_value

    return current_keys


def set_av_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Alphavantage key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_KEY_ALPHAVANTAGE", key, persist)
    status = check_av_key(show_output)

    return status


def check_av_key(show_output: bool = False) -> str:
    """Check Alpha Vantage key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME":  # pragma: allowlist secret
        logger.info("Alpha Vantage key not defined")
        status = "not defined"
    else:
        df = TimeSeries(
            key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
        ).get_intraday(symbol="AAPL")
        if df[0].empty:  # pylint: disable=no-member
            logger.warning("Alpha Vantage key defined, test failed")
            status = "defined, test failed"
        else:
            logger.info("Alpha Vantage key defined, test passed")
            status = "defined, test passed"

    if show_output:
        console.print(status + "\n")

    return status


def set_fmp_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Financial Modeling Prep key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_KEY_FINANCIALMODELINGPREP", key, persist)
    status = check_fmp_key(show_output)

    return status


def check_fmp_key(show_output: bool = False) -> str:
    """Check Financial Modeling Prep key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if (
        cfg.API_KEY_FINANCIALMODELINGPREP == "REPLACE_ME"  # pragma: allowlist secret
    ):  # pragma: allowlist secret
        logger.info("Financial Modeling Prep key not defined")
        status = "not defined"
    else:
        r = requests.get(
            f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"
        )
        if r.status_code in [403, 401]:
            logger.warning("Financial Modeling Prep key defined, test failed")
            status = "defined, test failed"
        elif r.status_code == 200:
            logger.info("Financial Modeling Prep key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Financial Modeling Prep key defined, test inconclusive")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_quandl_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Quandl key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_KEY_QUANDL", key, persist)
    status = check_quandl_key(show_output)

    return status


def check_quandl_key(show_output: bool = False) -> str:
    """Check Quandl key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_KEY_QUANDL == "REPLACE_ME":  # pragma: allowlist secret
        logger.info("Quandl key not defined")
        status = "not defined"
    else:
        try:
            quandl.save_key(cfg.API_KEY_QUANDL)
            quandl.get_table(
                "ZACKS/FC",
                paginate=True,
                ticker=["AAPL", "MSFT"],
                per_end_date={"gte": "2015-01-01"},
                qopts={"columns": ["ticker", "per_end_date"]},
            )
            logger.info("Quandl key defined, test passed")
            status = "defined, test passed"
        except Exception as _:  # noqa: F841
            logger.exception("Quandl key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_polygon_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Polygon key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_POLYGON_KEY", key, persist)
    status = check_polygon_key(show_output)

    return status


def check_polygon_key(show_output: bool = False) -> str:
    """Check Polygon key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_POLYGON_KEY == "REPLACE_ME":
        logger.info("Polygon key not defined")
        status = "not defined"
    else:
        r = requests.get(
            "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17"
            f"?apiKey={cfg.API_POLYGON_KEY}"
        )
        if r.status_code in [403, 401]:
            logger.warning("Polygon key defined, test failed")
            status = "defined, test failed"
        elif r.status_code == 200:
            logger.info("Polygon key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Polygon key defined, test inconclusive")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_fred_key(key: str, persist: bool = False, show_output: bool = False) -> str:
    """Set FRED key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_FRED_KEY", key, persist)
    status = check_fred_key(show_output)

    return status


def check_fred_key(show_output: bool = False) -> str:
    """Check FRED key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    if cfg.API_FRED_KEY == "REPLACE_ME":
        logger.info("FRED key not defined")
        status = "not defined"
    else:
        r = requests.get(
            f"https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={cfg.API_FRED_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            logger.warning("FRED key defined, test failed")
            status = "defined, test failed"
        elif r.status_code == 200:
            logger.info("FRED key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("FRED key defined, test inconclusive")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_news_key(key: str, persist: bool = False, show_output: bool = False):
    """Set News key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_NEWS_TOKEN", key, persist)
    status = check_news_key(show_output)

    return status


def check_news_key(show_output: bool = False) -> str:
    """Check News key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_NEWS_TOKEN == "REPLACE_ME":  # nosec
        logger.info("News API key not defined")
        status = "not defined"
    else:
        r = requests.get(
            f"https://newsapi.org/v2/everything?q=keyword&apiKey={cfg.API_NEWS_TOKEN}"
        )
        if r.status_code in [401, 403]:
            logger.warning("News API key defined, test failed")
            status = "defined, test failed"
        elif r.status_code == 200:
            logger.info("News API key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("News API key defined, test inconclusive")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_tradier_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Tradier key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_TRADIER_TOKEN", key, persist)
    status = check_tradier_key(show_output)

    return status


def check_tradier_key(show_output: bool = False) -> str:
    """Check Tradier key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_TRADIER_TOKEN == "REPLACE_ME":  # nosec
        logger.info("Tradier key not defined")
        status = "not defined"
    else:
        r = requests.get(
            "https://sandbox.tradier.com/v1/markets/quotes",
            params={"symbols": "AAPL"},
            headers={
                "Authorization": f"Bearer {cfg.API_TRADIER_TOKEN}",
                "Accept": "application/json",
            },
        )
        if r.status_code in [401, 403]:
            logger.warning("Tradier key not defined, test failed")
            status = "defined, test failed"
        elif r.status_code == 200:
            logger.info("Tradier key not defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Tradier key not defined, test inconclusive")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_cmc_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Coinmarketcap key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_CMC_KEY", key, persist)
    status = check_cmc_key(show_output)

    return status


def check_cmc_key(show_output: bool = False) -> str:
    """Check Coinmarketcap key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_CMC_KEY == "REPLACE_ME":
        logger.info("Coinmarketcap key not defined")
        status = "not defined"
    else:
        cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)

        try:
            cmc.cryptocurrency_map()
            logger.info("Coinmarketcap key defined, test passed")
            status = "defined, test passed"
        except CoinMarketCapAPIError:
            logger.exception("Coinmarketcap key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_finnhub_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Finnhub key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_FINNHUB_KEY", key, persist)
    status = check_finnhub_key(show_output)

    return status


def check_finnhub_key(show_output: bool = False) -> str:
    """Check Finnhub key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_FINNHUB_KEY == "REPLACE_ME":
        logger.info("Finnhub key not defined")
        status = "not defined"
    else:
        r = r = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg.API_FINNHUB_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            logger.warning("Finnhub key defined, test failed")
            status = "defined, test failed"
        elif r.status_code == 200:
            logger.info("Finnhub key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Finnhub key defined, test inconclusive")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_iex_key(key: str, persist: bool = False, show_output: bool = False):
    """Set IEX Cloud key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_IEX_KEY", key, persist)
    status = check_iex_key(show_output)

    return status


def check_iex_key(show_output: bool = False) -> str:
    """Check IEX Cloud key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_IEX_TOKEN == "REPLACE_ME":  # nosec
        logger.info("IEX Cloud key not defined")
        status = "not defined"
    else:
        try:
            pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")
            logger.info("IEX Cloud key defined, test passed")
            status = "defined, test passed"
        except PyEXception:
            logger.exception("IEX Cloud key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_reddit_key(
    client_id: str,
    client_secret: str,
    password: str,
    username: str,
    useragent: str,
    persist: bool = False,
    show_output: bool = False,
):
    """Set Reddit key

    Parameters
    ----------
        client_id: str
        client_secret: str
        password: str
        username: str
        useragent: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_REDDIT_CLIENT_ID", client_id, persist)
    set_key("OPENBB_API_REDDIT_CLIENT_SECRET", client_secret, persist)
    set_key("OPENBB_API_REDDIT_PASSWORD", password, persist)
    set_key("OPENBB_API_REDDIT_USERNAME", username, persist)
    set_key("OPENBB_API_REDDIT_USER_AGENT", useragent, persist)

    status = check_reddit_key(show_output)

    return status


def check_reddit_key(show_output: bool = False) -> str:
    """Check Reddit key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

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
        status = "not defined"
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
            status = "defined, test passed"
        except (Exception, ResponseException):
            logger.warning("Reddit key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_bitquery_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Bitquery key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_BITQUERY_KEY", key, persist)
    status = check_bitquery_key(show_output)

    return status


def check_bitquery_key(show_output: bool = False) -> str:
    """Check Bitquery key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    bitquery = cfg.API_BITQUERY_KEY
    if "REPLACE_ME" in bitquery:
        logger.info("Bitquery key not defined")
        status = "not defined"
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
        r = requests.post(
            "https://graphql.bitquery.io", json={"query": query}, headers=headers
        )
        if r.status_code == 200:
            logger.info("Bitquery key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Bitquery key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_twitter_key(
    key: str,
    secret_key: str,
    bearer_token: str,
    persist: bool = False,
    show_output: bool = False,
):
    """Set Twitter key

    Parameters
    ----------
        key: str
        secret_key: str
        bearer_token: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_TWITTER_KEY", key, persist)
    set_key("OPENBB_API_TWITTER_SECRET_KEY", secret_key, persist)
    set_key("OPENBB_API_TWITTER_BEARER_TOKEN", bearer_token, persist)

    status = check_twitter_key(show_output)

    return status


def check_twitter_key(show_output: bool = False) -> str:
    """Check Twitter key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    twitter_keys = [
        cfg.API_TWITTER_KEY,
        cfg.API_TWITTER_SECRET_KEY,
        cfg.API_TWITTER_BEARER_TOKEN,
    ]
    if "REPLACE_ME" in twitter_keys:
        logger.info("Twitter key not defined")
        status = "not defined"
    else:
        params = {
            "query": "(\\$AAPL) (lang:en)",
            "max_results": "10",
            "tweet.fields": "created_at,lang",
        }
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            params=params,  # type: ignore
            headers={"authorization": "Bearer " + cfg.API_TWITTER_BEARER_TOKEN},
        )
        if r.status_code == 200:
            logger.info("Twitter key defined, test passed")
            status = "defined, test passed"
        elif r.status_code in [401, 403]:
            logger.warning("Twitter key defined, test failed")
            status = "defined, test failed"
        else:
            logger.warning("Twitter key defined, test failed")
            status = "defined, test inconclusive"

    if show_output:
        console.print(status + "\n")

    return status


def set_rh_key(
    username: str,
    password: str,
    persist: bool = False,
    show_output: bool = False,
):
    """Set Robinhood key

    Parameters
    ----------
        username: str
        password: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_RH_USERNAME", username, persist)
    set_key("OPENBB_RH_PASSWORD", password, persist)

    status = check_rh_key(show_output)

    return status


def check_rh_key(show_output: bool = False) -> str:
    """Check Robinhood key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    rh_keys = [cfg.RH_USERNAME, cfg.RH_PASSWORD]
    if "REPLACE_ME" in rh_keys:
        logger.info("Robinhood key not defined")
        status = "not defined"
    else:
        logger.info("Robinhood key defined, not tested")
        status = "defined, not tested"

    if show_output:
        console.print(status + "\n")

    return status


def set_degiro_key(
    username: str,
    password: str,
    secret: str = "",
    persist: bool = False,
    show_output: bool = False,
):
    """Set Degiro key

    Parameters
    ----------
        username: str
        password: str
        secret: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_DG_USERNAME", username, persist)
    set_key("OPENBB_DG_PASSWORD", password, persist)
    set_key("OPENBB_DG_TOTP_SECRET", secret, persist)

    status = check_degiro_key(show_output)

    return status


def check_degiro_key(show_output: bool = False) -> str:
    """Check Degiro key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    dg_keys = [cfg.DG_USERNAME, cfg.DG_PASSWORD, cfg.DG_TOTP_SECRET]
    if "REPLACE_ME" in dg_keys:
        logger.info("Degiro key not defined")
        status = "not defined"
    else:
        logger.info("Degiro key defined, not tested")
        status = "defined, not tested"

    if show_output:
        console.print(status + "\n")

    return status


def set_oanda_key(
    account: str,
    token: str,
    account_type: str = "",
    persist: bool = False,
    show_output: bool = False,
):
    """Set Oanda key

    Parameters
    ----------
        account: str
        token: str
        account_type: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_OANDA_ACCOUNT", account, persist)
    set_key("OPENBB_OANDA_TOKEN", token, persist)
    set_key("OPENBB_OANDA_ACCOUNT_TYPE", account_type, persist)

    status = check_oanda_key(show_output)

    return status


def check_oanda_key(show_output: bool = False) -> str:
    """Check Oanda key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    oanda_keys = [cfg.OANDA_TOKEN, cfg.OANDA_ACCOUNT]
    if "REPLACE_ME" in oanda_keys:
        logger.info("Oanda key not defined")
        status = "not defined"
    else:
        client = oanda_API(access_token=cfg.OANDA_TOKEN)
        account = cfg.OANDA_ACCOUNT
        try:
            parameters = {"instruments": "EUR_USD"}
            request = oandapyV20.endpoints.pricing.PricingInfo(
                accountID=account, params=parameters
            )
            client.request(request)
            logger.info("Oanda key defined, test passed")
            status = "defined, test passed"

        except V20Error as e:
            logger.exception(str(e))
            logger.info("Oanda key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_binance_key(
    key: str,
    secret: str,
    persist: bool = False,
    show_output: bool = False,
):
    """Set Binance key

    Parameters
    ----------
        key: str
        secret: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_BINANCE_KEY", key, persist)
    set_key("OPENBB_API_BINANCE_SECRET", secret, persist)

    status = check_binance_key(show_output)

    return status


def check_binance_key(show_output: bool = False) -> str:
    """Check Binance key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if "REPLACE_ME" in [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]:
        logger.info("Binance key not defined")
        status = "not defined"

    else:
        try:
            client = binance.Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
            candles = client.get_klines(
                symbol="BTCUSDT", interval=client.KLINE_INTERVAL_1DAY
            )
            if len(candles) > 0:
                logger.info("Binance key defined, test passed")
                status = "defined, test passed"
            else:
                logger.info("Binance key defined, test failed")
                status = "defined, test failed"
        except Exception:
            logger.info("Binance key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_si_key(
    token: str,
    persist: bool = False,
    show_output: bool = False,
):
    """Set Sentimentinvestor key.

    Parameters
    ----------
        token: str
        secret: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_SENTIMENTINVESTOR_TOKEN", token, persist)

    status = check_si_key(show_output)

    return status


def check_si_key(show_output: bool = False) -> str:
    """Check Sentimentinvestor key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    si_keys = [cfg.API_SENTIMENTINVESTOR_TOKEN]
    if "REPLACE_ME" in si_keys:
        logger.info("Sentiment Investor key not defined")
        status = "not defined"
    else:
        try:
            account = requests.get(
                f"https://api.sentimentinvestor.com/v1/trending"
                f"?token={cfg.API_SENTIMENTINVESTOR_TOKEN}"
            )
            if account.ok and account.json().get("success", False):
                logger.info("Sentiment Investor key defined, test passed")
                status = "defined, test passed"
            else:
                logger.warning("Sentiment Investor key defined, test failed")
                status = "defined, test failed"
        except Exception:
            logger.warning("Sentiment Investor key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_coinbase_key(
    key: str,
    secret: str,
    passphrase: str,
    persist: bool = False,
    show_output: bool = False,
):
    """Set Coinbase key

    Parameters
    ----------
        key: str
        secret: str
        passphrase: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_COINBASE_KEY", key, persist)
    set_key("OPENBB_API_COINBASE_SECRET", secret, persist)
    set_key("OPENBB_API_COINBASE_PASS_PHRASE", passphrase, persist)

    status = check_coinbase_key(show_output)

    return status


def check_coinbase_key(show_output: bool = False) -> str:
    """Check Coinbase key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if "REPLACE_ME" in [
        cfg.API_COINBASE_KEY,
        cfg.API_COINBASE_SECRET,
        cfg.API_COINBASE_PASS_PHRASE,
    ]:
        logger.info("Coinbase key not defined")
        status = "not defined"
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
            status = "defined, test failed"
        else:
            logger.info("Coinbase key defined, test passed")
            status = "defined, test passed"

    if show_output:
        console.print(status + "\n")

    return status


def set_walert_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Walert key

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_WHALE_ALERT_KEY", key, persist)
    status = check_walert_key(show_output)

    return status


def check_walert_key(show_output: bool = False) -> str:
    """Check Walert key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_WHALE_ALERT_KEY == "REPLACE_ME":
        logger.info("Walert key not defined")
        status = "not defined"
    else:
        url = (
            "https://api.whale-alert.io/v1/transactions?api_key="
            + cfg.API_WHALE_ALERT_KEY
        )
        try:
            response = requests.get(url, timeout=2)
            if not 200 <= response.status_code < 300:
                logger.warning("Walert key defined, test failed")
                status = "defined, test failed"
            else:
                logger.info("Walert key defined, test passed")
                status = "defined, test passed"
        except Exception:
            logger.exception("Walert key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_glassnode_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Glassnode key.

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_GLASSNODE_KEY", key, persist)
    status = check_glassnode_key(show_output)

    return status


def check_glassnode_key(show_output: bool = False) -> str:
    """Check Glassnode key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_GLASSNODE_KEY == "REPLACE_ME":
        logger.info("Glassnode key not defined")
        status = "not defined"
    else:
        url = "https://api.glassnode.com/v1/metrics/market/price_usd_close"

        parameters = {
            "api_key": cfg.API_GLASSNODE_KEY,
            "a": "BTC",
            "i": "24h",
            "s": str(1_614_556_800),
            "u": str(1_641_227_783_561),
        }

        r = requests.get(url, params=parameters)
        if r.status_code == 200:
            logger.info("Glassnode key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Glassnode key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_coinglass_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Coinglass key.

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_COINGLASS_KEY", key, persist)
    status = check_coinglass_key(show_output)

    return status


def check_coinglass_key(show_output: bool = False) -> str:
    """Check Coinglass key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_COINGLASS_KEY == "REPLACE_ME":
        logger.info("Coinglass key not defined")
        status = "not defined"
    else:
        url = "https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?&symbol=BTC&interval=0"

        headers = {"coinglassSecret": cfg.API_COINGLASS_KEY}

        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            logger.info("Coinglass key defined, test passed")
            status = "defined, test passed"
        else:
            logger.warning("Coinglass key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_cpanic_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Cpanic key.

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_CRYPTO_PANIC_KEY", key, persist)
    status = check_cpanic_key(show_output)

    return status


def check_cpanic_key(show_output: bool = False) -> str:
    """Check Cpanic key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_CRYPTO_PANIC_KEY == "REPLACE_ME":
        logger.info("cpanic key not defined")
        status = "not defined"
    else:
        crypto_panic_url = f"https://cryptopanic.com/api/v1/posts/?auth_token={cfg.API_CRYPTO_PANIC_KEY}&kind=all"
        response = requests.get(crypto_panic_url)

        if not 200 <= response.status_code < 300:
            logger.warning("cpanic key defined, test failed")
            status = "defined, test failed"
        try:
            logger.info("cpanic key defined, test passed")
            status = "defined, test passed"
        except Exception as _:  # noqa: F841
            logger.warning("cpanic key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_ethplorer_key(key: str, persist: bool = False, show_output: bool = False):
    """Set Ethplorer key.

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_ETHPLORER_KEY", key, persist)
    status = check_cpanic_key(show_output)

    return status


def check_ethplorer_key(show_output: bool = False) -> str:
    """Check Ethplorer key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_ETHPLORER_KEY == "REPLACE_ME":
        logger.info("ethplorer key not defined")
        status = "not defined"
    else:
        ethplorer_url = "https://api.ethplorer.io/getTokenInfo/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984?apiKey="
        ethplorer_url += cfg.API_ETHPLORER_KEY
        response = requests.get(ethplorer_url)
        try:
            if response.status_code == 200:
                logger.info("ethplorer key defined, test passed")
                status = "defined, test passed"
            else:
                logger.warning("ethplorer key defined, test failed")
                status = "defined, test failed"
        except Exception as _:  # noqa: F841
            logger.exception("ethplorer key defined, test failed")
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_smartstake_key(
    key: str, token: str, persist: bool = False, show_output: bool = False
):
    """Set Smartstake key.

    Parameters
    ----------
        key: str
            API key
        token: str
            API token
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_SMARTSTAKE_KEY", key, persist)
    set_key("OPENBB_API_SMARTSTAKE_TOKEN", token, persist)
    status = check_smartstake_key(show_output)

    return status


def check_smartstake_key(show_output: bool = False) -> str:
    """Check Smartstake key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if "REPLACE_ME" in [
        cfg.API_SMARTSTAKE_TOKEN,
        cfg.API_SMARTSTAKE_KEY,
    ]:
        status = "not defined"
    else:
        payload = {
            "type": "history",
            "dayCount": 30,
            "key": cfg.API_SMARTSTAKE_KEY,
            "token": cfg.API_SMARTSTAKE_TOKEN,
        }

        smartstake_url = "https://prod.smartstakeapi.com/listData?app=TERRA"
        response = requests.get(smartstake_url, params=payload)  # type: ignore

        try:
            if response.status_code == 200:
                status = "defined, test passed"
            else:
                status = "defined, test failed"
        except Exception as _:  # noqa: F841
            status = "defined, test failed"

    if show_output:
        console.print(status + "\n")

    return status


def set_github_key(key: str, persist: bool = False, show_output: bool = False):
    """Set GitHub key.

    Parameters
    ----------
        key: str
            API key
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive
    """

    set_key("OPENBB_API_GITHUB_KEY", key, persist)
    status = check_github_key(show_output)

    return status


def check_github_key(show_output: bool = False) -> str:
    """Check GitHub key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    str
        API key status. One of the following:
            not defined
            defined, test failed
            defined, test passed
            defined, test inconclusive

    """

    if cfg.API_GITHUB_KEY == "REPLACE_ME":  # pragma: allowlist secret
        logger.info("GitHub key not defined")
        status = "not defined"
    else:
        status = "defined"
        # github api will not fail for the first requests without key
        # only after certain amount of requests the user will get rate limited

    if show_output:
        console.print(status + "\n")

    return status
