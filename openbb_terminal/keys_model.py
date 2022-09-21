import logging
import os
from typing import Dict
import dotenv
import quandl
import requests
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from openbb_terminal import config_terminal as cfg
from openbb_terminal.core.config.paths import USER_ENV_FILE
from openbb_terminal.rich_config import console

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


def set_key(env_var_name: str, env_var_value: str, local: bool = True) -> None:
    """Set API key.

    Parameters
    ----------
        env_var_name: str
            API name
        env_var_value: str
            API key
        local: bool
            If True, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If False, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.
    """
    if not local:
        os.environ[env_var_name] = env_var_value
        dotenv.set_key(str(USER_ENV_FILE), env_var_name, env_var_value)

    # Remove OPENBB_ prefix from env_var
    env_var_name = env_var_name[7:]

    # Set cfg.env_var_name = env_var_value
    # cfg.API_FRED_KEY = env_var_value
    setattr(cfg, env_var_name, env_var_value)


def get_keys() -> Dict:
    """Get dictionary with currently set API keys.

    Returns:
        Dict: key: API -> values: KEY.
    """

    # TODO: Output only the api environment variables. Remove settings variables.

    df = pd.read_csv(str(USER_ENV_FILE), delimiter="=", header=None)
    df = df.rename(columns={0: "API", 1: "KEY"})
    df = df.set_index("API")
    df["KEY"] = df["KEY"].apply(lambda x: x[1:-1])
    current_keys = df.to_dict().get("KEY")

    for env_var_name, env_var_value in current_keys.items():
        # Remove OPENBB_ prefix from env_var
        cfg_var_name = env_var_name[7:]

        # Check if api variable name is in cfg file
        if cfg_var_name in dir(cfg):
            cfg_var_value = getattr(cfg, cfg_var_name)
            # Substitute api key for cfg_var_value (will be different if you change it on Jupyter without local)
            if cfg_var_value != env_var_value:
                current_keys[env_var_name] = cfg_var_value

    return current_keys


def set_fred_key(key: str, local: bool = True, show_output: bool = False) -> str:
    """Set FRED key.

    Parameters
    ----------
        key: str
            API key
        local: bool
            If True, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If False, api key change will be global, i.e. it will affect terminal environment variables.
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

    set_key("OPENBB_API_FRED_KEY", key, local)
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


def set_av_key(key: str, local: bool = True, show_output: bool = False):
    """Set Alphavantage key.

    Parameters
    ----------
        key: str
            API key
        local: bool
            If True, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If False, api key change will be global, i.e. it will affect terminal environment variables.
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

    set_key("OPENBB_API_KEY_ALPHAVANTAGE", key, local)
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


def set_fmp_key(key: str, local: bool = True, show_output: bool = False):
    """Set Financial Modeling Prep key.

    Parameters
    ----------
        key: str
            API key
        local: bool
            If True, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If False, api key change will be global, i.e. it will affect terminal environment variables.
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

    set_key("OPENBB_API_KEY_FINANCIALMODELINGPREP", key, local)
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


def set_quandl_key(key: str, local: bool = True, show_output: bool = False):
    """Set Quandl key.

    Parameters
    ----------
        key: str
            API key
        local: bool
            If True, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If False, api key change will be global, i.e. it will affect terminal environment variables.
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

    set_key("OPENBB_API_KEY_QUANDL", key, local)
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


def set_polygon_key(key: str, local: bool = True, show_output: bool = False):
    """Set Polygon key.

    Parameters
    ----------
        key: str
            API key
        local: bool
            If True, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If False, api key change will be global, i.e. it will affect terminal environment variables.
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

    set_key("OPENBB_API_POLYGON_KEY", key, local)
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