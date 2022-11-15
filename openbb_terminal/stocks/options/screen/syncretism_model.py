"""ops.syncretism.io model"""
__docformat__ = "numpy"

import configparser
import logging
from pathlib import Path
from typing import Dict, Tuple, Union

import pandas as pd
import requests
import yfinance as yf

from openbb_terminal.core.config.paths import USER_PRESETS_DIRECTORY
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import yfinance_model

logger = logging.getLogger(__name__)

accepted_orders = [
    "e_desc",
    "e_asc",
    "iv_desc",
    "iv_asc",
    "md_desc",
    "md_asc",
    "lp_desc",
    "lp_asc",
    "oi_asc",
    "oi_desc",
    "v_desc",
    "v_asc",
]


@log_start_end(log=logger)
def get_historical_greeks(
    symbol: str,
    expiry: str,
    strike: Union[str, float],
    chain_id: str = "",
    put: bool = False,
) -> pd.DataFrame:
    """Get histoical option greeks

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration date
    strike: Union[str, float]
        Strike price to look for
    chain_id: str
        OCC option symbol.  Overwrites other inputs
    put: bool
        Is this a put option?

    Returns
    -------
    df: pd.DataFrame
        Dataframe containing historical greeks
    """
    if isinstance(strike, str):
        try:
            strike = float(strike)
        except ValueError:
            console.print(
                f"[red]Strike of {strike} cannot be converted to a number.[/red]\n"
            )
            return pd.DataFrame()
    if not chain_id:
        options = yfinance_model.get_option_chain(symbol, expiry)

        if put:
            options = options.puts
        else:
            options = options.calls

        selection = options.loc[options.strike == strike, "contractSymbol"]
        try:
            chain_id = selection.values[0]
        except IndexError:
            console.print(f"[red]Strike price of {strike} not found.[/red]\n")
            return pd.DataFrame()

    r = requests.get(f"https://api.syncretism.io/ops/historical/{chain_id}")

    if r.status_code != 200:
        console.print("Error in request.")
        return pd.DataFrame()

    history = r.json()

    iv, delta, gamma, theta, rho, vega, premium, price, time = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    for entry in history:
        time.append(pd.to_datetime(entry["timestamp"], unit="s"))
        iv.append(entry["impliedVolatility"])
        gamma.append(entry["gamma"])
        delta.append(entry["delta"])
        theta.append(entry["theta"])
        rho.append(entry["rho"])
        vega.append(entry["vega"])
        premium.append(entry["premium"])
        price.append(entry["regularMarketPrice"])

    data = {
        "iv": iv,
        "gamma": gamma,
        "delta": delta,
        "theta": theta,
        "rho": rho,
        "vega": vega,
        "premium": premium,
        "price": price,
    }

    df = pd.DataFrame(data, index=time)
    return df


@log_start_end(log=logger)
def get_preset_choices() -> Dict:
    """
    Return a dict containing keys as name of preset and
    filepath as value
    """

    PRESETS_PATH = USER_PRESETS_DIRECTORY / "stocks" / "options"
    PRESETS_PATH_DEFAULT = Path(__file__).parent.parent / "presets"
    preset_choices = {
        filepath.name: filepath
        for filepath in PRESETS_PATH.iterdir()
        if filepath.suffix == ".ini"
    }
    preset_choices.update(
        {
            filepath.name: filepath
            for filepath in PRESETS_PATH_DEFAULT.iterdir()
            if filepath.suffix == ".ini"
        }
    )

    return preset_choices


@log_start_end(log=logger)
def get_screener_output(preset: str) -> Tuple[pd.DataFrame, str]:
    """Screen options based on preset filters

    Parameters
    ----------
    preset: str
        Chosen preset

    Returns
    -------
    Tuple[pd.DataFrame, str]
        DataFrame with screener data or empty if errors, String containing error message if supplied
    """
    d_cols = {
        "contractSymbol": "CS",
        "symbol": "S",
        "optType": "T",
        "strike": "Str",
        "expiration": "Exp ∨",
        "impliedVolatility": "IV",
        "lastPrice": "LP",
        "bid": "B",
        "ask": "A",
        "volume": "V",
        "openInterest": "OI",
        "yield": "Y",
        "monthlyyield": "MY",
        "regularMarketPrice": "SMP",
        "regularMarketDayLow": "SMDL",
        "regularMarketDayHigh": "SMDH",
        "lastTradeDate": "LU",
        "lastCrawl": "LC",
        "inTheMoney": "ITM",
        "pChange": "PC",
        "priceToBook": "PB",
    }

    preset_filter = configparser.RawConfigParser()
    preset_filter.optionxform = str  # type: ignore
    choices = get_preset_choices()
    if preset not in choices:
        return pd.DataFrame(), "No data found"
    preset_filter.read(choices[preset])

    d_filters = {k: v for k, v in dict(preset_filter["FILTER"]).items() if v}
    s_filters = str(d_filters)
    s_filters = (
        s_filters.replace(": '", ": ")
        .replace("',", ",")
        .replace("'}", "}")
        .replace("'", '"')
    )
    for order in accepted_orders:
        s_filters = s_filters.replace(f" {order}", f' "{order}"')

    errors = check_presets(d_filters)

    if errors:
        return pd.DataFrame(), errors

    link = "https://api.syncretism.io/ops"

    res = requests.get(
        link, headers={"Content-type": "application/json"}, data=s_filters
    )

    # pylint:disable=no-else-return
    if res.status_code == 200:
        df_res = pd.DataFrame(res.json())

        if df_res.empty:
            return df_res, f"No options data found for preset: {preset}"

        df_res = df_res.rename(columns=d_cols)[list(d_cols.values())[:17]]
        df_res["Exp ∨"] = df_res["Exp ∨"].apply(
            lambda x: pd.to_datetime(x, unit="s").strftime("%m-%d-%y")
        )
        df_res["LU"] = df_res["LU"].apply(
            lambda x: pd.to_datetime(x, unit="s").strftime("%m-%d-%y")
        )
        df_res["Y"] = df_res["Y"].round(3)
        df_res["MY"] = df_res["MY"].round(3)
        return df_res, ""

    else:
        return pd.DataFrame(), f"Request Error: {res.status_code}"


# pylint: disable=eval-used


@log_start_end(log=logger)
def check_presets(preset_dict: dict) -> str:
    """Checks option screener preset values

    Parameters
    ----------
    preset_dict: dict
        Defined presets from configparser

    Returns
    -------
    error: str
        String of all errors accumulated
    """
    float_list = [
        "min-iv",
        "max-iv",
        "min-oi",
        "max-oi",
        "min-strike",
        "max-strike",
        "min-volume",
        "max-volume",
        "min-voi",
        "max-voi",
        "min-diff",
        "max-diff",
        "min-ask-bid",
        "max-ask-bid",
        "min-exp",
        "max-exp",
        "min-price",
        "max-price",
        "min-price-20d",
        "max-price-20d",
        "min-volume-20d",
        "max-volume-20d",
        "min-iv-20d",
        "max-iv-20d",
        "min-delta-20d",
        "max-delta-20d",
        "min-gamma-20d",
        "max-gamma-20d",
        "min-theta-20d",
        "max-theta-20d",
        "min-vega-20d",
        "max-vega-20d",
        "min-rho-20d",
        "max-rho-20d",
        "min-price-100d",
        "max-price-100d",
        "min-volume-100d",
        "max-volume-100d",
        "min-iv-100d",
        "max-iv-100d",
        "min-delta-100d",
        "max-delta-100d",
        "min-gamma-100d",
        "max-gamma-100d",
        "min-theta-100d",
        "max-theta-100d",
        "min-vega-100d",
        "max-vega-100d",
        "min-rho-100d",
        "max-rho-100d",
        "min-sto",
        "max-sto",
        "min-yield",
        "max-yield",
        "min-myield",
        "max-myield",
        "min-delta",
        "max-delta",
        "min-gamma",
        "max-gamma",
        "min-theta",
        "max-theta",
        "min-vega",
        "max-vega",
        "min-cap",
        "max-cap",
    ]
    bool_list = ["active", "stock", "etf", "puts", "calls", "itm", "otm", "exclude"]
    error = ""
    for key, value in preset_dict.items():
        if key in float_list:
            try:
                float(value)
                if value.startswith("."):
                    error += f"{key} : {value} needs to be formatted with leading 0\n"
            except Exception:
                error += f"{key} : {value}, should be float\n"

        elif key in bool_list:
            if value not in ["true", "false"]:
                error += f"{key} : {value},  Should be [true/false]\n"

        elif key == "tickers":
            for symbol in value.split(","):
                try:
                    if yf.Ticker(eval(symbol)).info["regularMarketPrice"] is None:
                        error += f"{key} : {symbol} not found on yfinance"

                except NameError:
                    error += f"{key} : {value}, {symbol} failed"

        elif key == "limit":
            try:
                int(value)
            except Exception:
                error += f"{key} : {value} , should be integer\n"

        elif key == "order-by":
            if value.replace('"', "") not in accepted_orders:
                error += f"{key} : {value} not accepted ordering\n"
    if error:
        logging.exception(error)
    return error
