# pylint: disable=C0302, R0911, W0612, R0912
""" Options Chains Module """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
from copy import deepcopy

# IMPORTATION THIRDPARTY
from typing import Any, Optional

import numpy as np
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.cboe_model import load_options as load_cboe
from openbb_terminal.stocks.options.intrinio_model import load_options as load_intrinio
from openbb_terminal.stocks.options.nasdaq_model import load_options as load_nasdaq
from openbb_terminal.stocks.options.op_helpers import Options
from openbb_terminal.stocks.options.tmx_model import load_options as load_tmx
from openbb_terminal.stocks.options.tradier_model import load_options as load_tradier
from openbb_terminal.stocks.options.yfinance_model import load_options as load_yfinance

logger = logging.getLogger(__name__)

SOURCES = ["CBOE", "YahooFinance", "Tradier", "Intrinio", "Nasdaq", "TMX"]

# mypy: disable-error-code="attr-defined, index"


@log_start_end(log=logger)
def load_options_chains(
    symbol: str,
    source: str = "CBOE",
    date: str = "",
    pydantic: bool = False,
) -> Options:
    """Loads all options chains from a specific source, fields returned to each attribute will vary.

    Parameters
    ----------
    symbol : str
        The underlying asset's symbol.
    source: str
        The source of the data. Choices are "CBOE", "YahooFinance", "Tradier", "Intrinio", "Nasdaq", or "TMX".
    date: Optional[str]
        The date for the EOD option chain.  Format: YYYY-MM-DD.
        This parameter is only available for "TMX" or "Intrinio".
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas object.  Default is False.

    Returns
    -------
    Options: Options data object

        chains: dict
            All options chains data from a specific source.  Returns as a Pandas DataFrame if pydantic is False.
        expirations: list[str]
            List of all unique expiration dates.
        hasGreeks: bool
            True if the source returns greeks with the chains data.
        hasIV: bool
            True if the source returns implied volatility with the chains data.
        last_price: float
            The last price (or the price at the EOD for the date.of the EOD option chain).
        source: str
            The source that was entered in the input.
        strikes: list[float]
            List of all unique strike prices.
        symbol: str
            The symbol that was entered in the input.
        SYMBOLS: pd.DataFrame
            The symbol directory to the selected source, when available.  Only returned when pydantic is False.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: dict
            The underlying asset's price and performance.  Returns as a Pandas Series if pydantic is False.

    Examples
    --------
    Loads SPY data from CBOE, returns as a Pydantic Model, and displays the longest-dated expiration chain.

    >>> from openbb_terminal.sdk import openbb
    >>> import pandas as pd
    >>> data = openbb.stocks.options.load_options_chains("SPY", pydantic = True)
    >>> chains = pd.DataFrame(data.chains)
    >>> chains[chains["expiration"] == data.expirations[-1]]

    Loads QQQ data from Tradier as a Pydantic Model.

    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains("QQQ", source = "Tradier", pydantic = True)

    Loads VIX data from YahooFinance as a Pandas object.

    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains("^VIX", source = "YahooFinance")

    Loads XIU data from TMX and displays the 25 highest open interest options.

    >>> from openbb_terminal.sdk  import openbb
    >>> data = openbb.stocks.options.load_options_chains("XIU", "TMX")
    >>> data.chains.sort_values("openInterest", ascending=False).head(25)

    Loads the EOD chains data for XIU.TO from March 15, 2020, sorted by number of transactions.

    >>> from openbb_terminal.sdk  import openbb
    >>> data = openbb.stocks.options.load_options_chains("XIU.TO", "TMX", "2020-03-15")
    >>> data.chains.sort_values("transactions", ascending=False).head(25)
    """

    if source not in SOURCES:
        console.print("Invalid choice. Choose from: ", list(SOURCES), sep=None)
        return Options()

    if source == "Nasdaq":
        return load_nasdaq(symbol, pydantic)
    if source == "YahooFinance":
        return load_yfinance(symbol, pydantic)
    if source == "Tradier":
        return load_tradier(symbol, pydantic)
    if source == "TMX":
        if date != "":
            return load_tmx(symbol, date, pydantic)
        return load_tmx(symbol, pydantic=pydantic)
    if source == "Intrinio":
        if date != "":
            return load_intrinio(symbol, date, pydantic)
        return load_intrinio(symbol, pydantic=pydantic)

    return load_cboe(symbol, pydantic)


def validate_object(  # noqa: PLR0911
    options: Options, scope: Optional[str] = "object", days: Optional[int] = None
) -> Any:
    """This is an internal helper function for validating the Options data object passed
    through the input of functions defined in the OptionsChains class.  The purpose is to handle
    multi-type inputs with backwards compatibility and provide robust error handling.  The return
    is the portion of the object, or a true/false validation, required to perform the operation.

    Parameters
    ----------
    options : object
        The Options data object.
        Accepts both Pydantic and Pandas object types, as defined by `load_options_chains()`.
        A Pandas DataFrame, or dictionary, with the options chains data is also accepted.
    scope: str
        The scope of the data needing to be validated.  Choices are: ["chains", "object", "strategies", "nonZeroPrices"]
    days: int
        The number of target number of days until the expiration.

    Returns
    -------
    Any:
        if scope == "chains":
            pd.DataFrame
                Pandas DataFrame with the validated data.
        if scope == "object" or scope == "strategies":
            bool
                True if the object is a valid Options data object.

    Examples
    --------
    Load some data first:
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains("SPY")
    To extract just the chains data, use:
    >>> chains = options_chains_model.validate_object(data, scope="chains")
    To pass as a true/false validation, use:
    >>> if options_chains_model.validate_object(data, scope="object") is False:
    >>>     return
    To pass and return the entire object for non-zero prices:
    >>> if options_chains_model.validate_object(data, scope="object") is True:
    >>>     data = options_chains_model.validate_object(data, scope="nonZeroPrices")
    """

    scopes = ["chains", "object", "strategies", "nonZeroPrices"]

    scope = scope or "chains"

    if scope not in scopes:
        console.print("Invalid choice.  The supported methods are:", scopes)
        return pd.DataFrame()

    if scope == "object":
        try:
            if (
                isinstance(options.strikes, list)
                and isinstance(options.expirations, list)
                and hasattr(options, "last_price")
            ):
                return True

        except AttributeError:
            console.print(
                "Error: Invalid data type supplied.  The Options data object is required.  "
                "Use load_options_chains() first."
            )
            return False

    if scope == "strategies":
        try:
            if isinstance(options.last_price, float):
                return True
        except AttributeError:
            console.print(
                "`last_price` was not found in the OptionsChainsData object and is required for this operation."
            )
            return False

    if scope == "chains":
        try:
            if isinstance(options, pd.DataFrame):
                chains = options.copy()

            if isinstance(options, dict):
                chains = pd.DataFrame(options)

            elif isinstance(options, object) and not isinstance(options, pd.DataFrame):
                chains = (
                    pd.DataFrame(options.chains)  # type: ignore[attr-defined]
                    if isinstance(options.chains, dict)  # type: ignore[attr-defined]
                    else options.chains.copy()  # type: ignore[attr-defined]
                )

                if options is None or chains.empty:
                    console.print(
                        "No options chains data found in the supplied object.  Use load_options_chains()."
                    )
                    return pd.DataFrame()

            if "openInterest" not in chains.columns:
                console.print("Expected column, openInterest, not found.")
                return pd.DataFrame()

            if "volume" not in chains.columns:
                console.print("Expected column, volume, not found.")
                return pd.DataFrame()
        except AttributeError:
            console.print("Error: Invalid data type supplied.")
            return pd.DataFrame()

        return chains

    if scope == "nonZeroPrices":
        dte_estimate = get_nearest_dte(  # noqa:F841 pylint: disable=unused-variable
            options, days
        )
        # When Intrinio data is not EOD, there is no "ask" column, renaming "close".
        if (
            options.source == "Intrinio"
            and options.date is None
            or options.source == "Intrinio"
            and options.date == ""
        ):
            options.chains["ask"] = options.chains["close"]
            options.chains["bid"] = options.chains["close"]

        # Error handling for TMX EOD data when the date is an expiration date.  EOD, 0-day options are excluded.
        if options.source == "TMX" and options.date != "":
            options.chains = options.chains[options.chains["dte"] > 0]

        if (
            options.source == "TMX"
            and options.date is None
            or options.source == "TMX"
            and options.date == ""
        ):
            options.chains["ask"] = options.chains["lastPrice"]
            options.chains["bid"] = options.chains["lastPrice"]

        if (
            options.source == "TMX"
            or options.source == "YahooFinance"
            or options.source == "Nasdaq"
            and options.chains.query("`dte` == @dte_estimate")["ask"].sum() == 0
        ):
            options.chains["ask"] = options.chains["lastPrice"]
        if (
            options.source == "TMX"
            or options.source == "YahooFinance"
            or options.source == "Nasdaq"
            and options.chains.query("`dte` == @dte_estimate")["bid"].sum() == 0
        ):
            options.chains["bid"] = options.chains["lastPrice"]

        return options

    console.print(
        "Error: No valid data supplied. Check the input to ensure it is not empty or None."
    )

    return False


def get_nearest_expiration(options: Options, expiration: Optional[str] = "") -> str:
    """Gets the closest expiration date to the target date."""

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    _expirations = pd.Series(pd.to_datetime(options.expirations))
    _expiration = pd.to_datetime(expiration)
    _nearest = pd.DataFrame(_expirations - _expiration)
    _nearest_exp = abs(_nearest[0].astype("int64")).idxmin()

    return options.expirations[_nearest_exp]


def get_nearest_dte(options: Options, days: Optional[int] = 30) -> int:
    """Gets the closest expiration date to the target number of days until expiry.

    Parameters
    ----------
    options : object
        The Options data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.

    Returns
    -------
    int
        The closest expiration date to the target number of days until expiry, expressed as DTE.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains("QQQ")
    >>> options_chains_model.get_nearest_dte(data, 42)
    >>> options_chains_model.get_nearest_dte(data, 90)
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    days = -1 if days == 0 else days

    nearest = (options.chains["dte"] - days).abs().idxmin()

    return options.chains.loc[nearest]["dte"]


def get_nearest_call_strike(
    options: Options, days: Optional[int] = 30, strike_price: Optional[float] = 0
) -> float:
    """Gets the closest call strike to the target price and number of days until expiry.

    Parameters
    ----------
    options : object
        The Options data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.
    strike_price: float
        The target strike price.  Default is the last price of the underlying stock.

    Returns
    -------
    float
        The closest strike price to the target price and number of days until expiry.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains("SPY")
    >>> options_chains_model.get_nearest_call_strike(data)
    >>> options_chains_model.get_nearest_call_strike(data, 180, 427)
    >>> days = data.chains.dte.unique().tolist()
    >>> for day in days:
    >>>     print(get_nearest_call_strike(data, day))
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if strike_price == 0:
        strike_price = options.last_price

    dte_estimate = get_nearest_dte(options, days)

    if (
        len(
            options.chains[options.chains["dte"] == dte_estimate].query(
                "`optionType` == 'call'"
            )
        )
        == 0
    ):
        return pd.DataFrame()

    nearest = (
        (
            options.chains[options.chains["dte"] == dte_estimate]
            .query("`optionType` == 'call'")
            .convert_dtypes()["strike"]
            - strike_price
        )
        .abs()
        .idxmin()
    )

    return options.chains.loc[nearest]["strike"]


def get_nearest_put_strike(
    options: Options, days: Optional[int] = 30, strike_price: Optional[float] = 0
) -> float:
    """Gets the closest put strike to the target price and number of days until expiry.

    Parameters
    ----------
    options : object
        The Options data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.
    strike_price: float
        The target strike price.  Default is the last price of the underlying stock.

    Returns
    -------
    float
        The closest strike price to the target price and number of days until expiry.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains('SPY')
    >>> options_chains_model.get_nearest_put_strike(data, 90, 402)
    >>> options_chains_model.get_nearest_put_strike(data, 90)
    >>> days = data.chains.dte.unique().tolist()
    >>> for day in days:
    >>>     print(get_nearest_put_strike(data, day))
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if strike_price == 0:
        strike_price = options.last_price

    dte_estimate = get_nearest_dte(options, days)

    if (
        len(
            options.chains[options.chains["dte"] == dte_estimate].query(
                "`optionType` == 'put'"
            )
        )
        == 0
    ):
        return pd.DataFrame()

    nearest = (
        (
            options.chains[options.chains["dte"] == dte_estimate]
            .query("`optionType` == 'put'")
            .convert_dtypes()["strike"]
            - strike_price
        )
        .abs()
        .idxmin()
    )

    return options.chains.loc[nearest]["strike"]


def get_nearest_otm_strike(
    options: Options, moneyness: Optional[float] = 5
) -> dict[str, float]:
    """Gets the nearest put and call strikes at a given percent OTM from the underlying price.

    Parameters
    ----------
    options : OptionsChains
        The Options data object.  Use load_options_chains() to load the data.
    moneyness: float
        The target percent OTM, expressed as a percent between 0 and 100.  Default is 5.

    Returns
    -------
    dict[str, float]
        Dictionary of the upper (call) and lower (put) strike prices.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains('SPY')
    >>> strikes = options_chains_model.get_nearest_otm_strike(data, 5)
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if not moneyness:
        moneyness = 5

    if 0 < moneyness < 100:
        moneyness = moneyness / 100

    if moneyness > 100 or moneyness < 0:
        console.print(
            "Error: Moneyness must be expressed as a percentage between 0 and 100"
        )
        return {}

    upper = options.last_price * (1 + moneyness)
    lower = options.last_price * (1 - moneyness)
    strikes = pd.Series(options.strikes)
    nearest_call = (upper - strikes).abs().idxmin()
    call = strikes[nearest_call]
    nearest_putt = (lower - strikes).abs().idxmin()
    put = strikes[nearest_putt]

    otmStrikes = {"call": call, "put": put}

    return otmStrikes


def calculate_straddle(
    options: Options,
    days: Optional[int] = 30,
    strike: float = 0,
) -> pd.DataFrame:
    """Calculates the cost of a straddle and its payoff profile. Use a negative strike price for short options.
    Requires the Options data object.

    Parameters
    ----------
    options : object
        The Options data object. Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry. Default is 30 days.
    strike: float
        The target strike price. Enter a negative value for short options.
        Default is the last price of the underlying stock.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results. Strike1 is the nearest call strike, strike2 is the nearest put strike.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains('SPY')
    >>> openbb.stocks.options.calculate_straddle(data)
    """
    options = deepcopy(options)
    if not days:
        days = 30
    if days and days == 0:
        days = -1

    short: bool = False
    if strike is not None and strike < 0:
        short = True
    strike_price = abs(strike)

    bidAsk = "bid" if short else "ask"  # noqa:F841

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841

    options = validate_object(options, "nonZeroPrices", dte_estimate)

    if not strike_price:
        strike_price = options.last_price

    call_strike_estimate = get_nearest_call_strike(
        options, dte_estimate, strike_price
    )  # noqa:F841
    put_strike_estimate = get_nearest_put_strike(
        options, dte_estimate, strike_price
    )  # noqa:F841

    call_premium = options.chains.query(
        "`strike` == @call_strike_estimate and `dte` == @dte_estimate and `optionType` == 'call'"
    )[bidAsk].values

    put_premium = options.chains.query(
        "`strike` == @put_strike_estimate and `dte` == @dte_estimate and `optionType` == 'put'"
    )[bidAsk].values

    straddle_cost = call_premium + put_premium

    straddle: dict[str, Any] = {}

    # Include the as-of date if the data is historical EOD.
    if (
        options.source == "Intrinio"
        and options.date != ""
        or options.source == "TMX"
        and options.date != ""
    ):
        straddle.update({"Date": options.date})

    straddle.update(
        {
            "Symbol": options.symbol,
            "Underlying Price": options.last_price,
            "Expiration": options.chains.query("`dte` == @dte_estimate")[
                "expiration"
            ].unique()[0],
            "DTE": dte_estimate,
            "Strike 1": call_strike_estimate,
            "Strike 2": put_strike_estimate,
            "Strike 1 Premium": call_premium[0],
            "Strike 2 Premium": put_premium[0],
            "Cost": straddle_cost[0] * -1 if short else straddle_cost[0],
            "Cost Percent": round(
                straddle_cost[0] / options.last_price * 100, ndigits=4
            ),
            "Breakeven Upper": call_strike_estimate + straddle_cost[0],
            "Breakeven Upper Percent": round(
                (call_strike_estimate + straddle_cost[0]) / options.last_price * 100,
                ndigits=4,
            )
            - 100,
            "Breakeven Lower": put_strike_estimate - straddle_cost[0],
            "Breakeven Lower Percent": -100
            + round(
                (put_strike_estimate - straddle_cost[0]) / options.last_price * 100,
                ndigits=4,
            ),
            "Max Profit": abs(straddle_cost[0]) if short else np.inf,
            "Max Loss": np.inf if short else straddle_cost[0] * -1,
        }
    )

    straddle = pd.DataFrame(data=straddle.values(), index=straddle.keys()).rename(
        columns={0: "Short Straddle" if short else "Long Straddle"}
    )

    straddle.loc["Payoff Ratio"] = round(
        abs(straddle.loc["Max Profit"][0] / straddle.loc["Max Loss"][0]), ndigits=4
    )

    return straddle


def calculate_strangle(
    options: Options,
    days: Optional[int] = 30,
    moneyness: Optional[float] = 5,
) -> pd.DataFrame:
    """Calculates the cost of a strangle and its payoff profile.  Use a negative value for moneyness for short options.

    Requires the Options data object.

    Parameters
    ----------
    options : object
        The Options data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.
    moneyness: float
        The percentage of OTM moneyness, expressed as a percent between -100 < 0 < 100.
        Enter a negative number for short options.
        Default is 5.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results. Strike 1 is the nearest call strike, and strike 2 is the nearest put strike.

    Examples
    --------
    >>> data = openbb.stocks.options.load_options_chains("SPY")
    >>> data.calculate_strangle()
    """

    options = deepcopy(options)

    if not days:
        days = 30

    if not moneyness:
        moneyness = 5

    short: bool = False

    if moneyness < 0:
        short = True
    moneyness = abs(moneyness)
    bidAsk = "bid" if short else "ask"  # noqa:F841

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841

    options = validate_object(options, "nonZeroPrices", dte_estimate)

    if moneyness > 100 or moneyness < 0:
        console.print("Error: Moneyness must be between 0 and 100.")
        return pd.DataFrame()

    strikes = get_nearest_otm_strike(options, moneyness)

    call_strike_estimate = get_nearest_call_strike(
        options, dte_estimate, strikes["call"]
    )  # noqa:F841
    put_strike_estimate = get_nearest_put_strike(
        options, dte_estimate, strikes["put"]
    )  # noqa:F841

    call_premium = options.chains.query(
        "`strike` == @call_strike_estimate and `dte` == @dte_estimate and `optionType` == 'call'"
    )[bidAsk].values

    put_premium = options.chains.query(
        "`strike` == @put_strike_estimate and `dte` == @dte_estimate and `optionType` == 'put'"
    )[bidAsk].values

    strangle_cost = call_premium + put_premium

    strangle: dict[str, Any] = {}

    # Includees the as-of date if it is historical EOD data.
    if (
        options.source == "Intrinio"
        and options.date != ""
        or options.source == "TMX"
        and options.date != ""
    ):
        strangle.update({"Date": options.date})

    strangle.update(
        {
            "Symbol": options.symbol,
            "Underlying Price": options.last_price,
            "Expiration": options.chains.query("`dte` == @dte_estimate")[
                "expiration"
            ].unique()[0],
            "DTE": dte_estimate,
            "Strike 1": call_strike_estimate,
            "Strike 2": put_strike_estimate,
            "Strike 1 Premium": call_premium[0],
            "Strike 2 Premium": put_premium[0],
            "Cost": strangle_cost[0] * -1 if short else strangle_cost[0],
            "Cost Percent": round(
                strangle_cost[0] / options.last_price * 100, ndigits=4
            ),
            "Breakeven Upper": call_strike_estimate + strangle_cost[0],
            "Breakeven Upper Percent": round(
                (call_strike_estimate + strangle_cost[0]) / options.last_price * 100,
                ndigits=4,
            )
            - 100,
            "Breakeven Lower": put_strike_estimate - strangle_cost[0],
            "Breakeven Lower Percent": -100
            + round(
                (put_strike_estimate - strangle_cost[0]) / options.last_price * 100,
                ndigits=4,
            ),
            "Max Profit": abs(strangle_cost[0]) if short else np.inf,
            "Max Loss": np.inf if short else strangle_cost[0] * -1,
        }
    )

    strangle = pd.DataFrame(data=strangle.values(), index=strangle.keys()).rename(
        columns={0: "Short Strangle" if short else "Long Strangle"}
    )

    strangle.loc["Payoff Ratio"] = round(
        abs(strangle.loc["Max Profit"][0] / strangle.loc["Max Loss"][0]), ndigits=4
    )

    return strangle


def calculate_vertical_call_spread(
    options: Options,
    days: Optional[int] = 30,
    sold_strike: Optional[float] = 0,
    bought_strike: Optional[float] = 0,
) -> pd.DataFrame:
    """Calculates the vertical call spread for the target DTE.
    A bull call spread is when the sold strike is above the bought strike.

    Parameters
    ----------
    options : object
        The Options data object. Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry. This value will be used to get the nearest valid DTE.
        Default is 30 days.
    sold_strike: float
        The target strike price for the short leg of the vertical call spread.
        Default is the 5% OTM above the last price of the underlying.
    bought_strike: float
        The target strike price for the long leg of the vertical call spread. Default is the last price of the underlying.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results. Strike 1 is the sold strike, and strike 2 is the bought strike.

    Examples
    --------
    Load the data:
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains()
    >>> data = op.load_options_chains("QQQ")

    For a bull call spread:
    >>> data.calculate_vertical_call_spread(days=10, sold_strike=355, bought_strike=350)

    For a bear call spread:
    >>> data.calculate_vertical_call_spread(days=10, sold_strike=350, bought_strike=355)
    """

    options = deepcopy(options)

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if not days:
        days = 30

    if not bought_strike:
        bought_strike = options.last_price * 1.0250

    if not sold_strike:
        sold_strike = options.last_price * 1.0750

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841

    options = validate_object(options, "nonZeroPrices", dte_estimate)

    sold = get_nearest_call_strike(options, days, sold_strike)
    bought = get_nearest_call_strike(options, days, bought_strike)

    sold_premium = options.chains.query(
        "`strike` == @sold and `dte` == @dte_estimate and `optionType` == 'call'"
    )["bid"].values * (-1)
    bought_premium = options.chains.query(
        "`strike` == @bought and `dte` == @dte_estimate and `optionType` == 'call'"
    )["ask"].values

    spread_cost = bought_premium + sold_premium
    breakeven_price = bought + spread_cost[0]
    max_profit = sold - bought - spread_cost[0]
    call_spread_: dict[str, Any] = {}
    if sold != bought and spread_cost[0] != 0:
        # Includees the as-of date if it is historical EOD data.
        if (
            options.source == "Intrinio"
            and options.date != ""
            or options.source == "TMX"
            and options.date != ""
        ):
            call_spread_.update({"Date": options.date})

        call_spread_.update(
            {
                "Symbol": options.symbol,
                "Underlying Price": options.last_price,
                "Expiration": options.chains.query("`dte` == @dte_estimate")[
                    "expiration"
                ].unique()[0],
                "DTE": dte_estimate,
                "Strike 1": sold,
                "Strike 2": bought,
                "Strike 1 Premium": sold_premium[0],
                "Strike 2 Premium": bought_premium[0],
                "Cost": spread_cost[0],
                "Cost Percent": round(
                    spread_cost[0] / options.last_price * 100, ndigits=4
                ),
                "Breakeven Lower": breakeven_price,
                "Breakeven Lower Percent": round(
                    (breakeven_price / options.last_price * 100) - 100, ndigits=4
                ),
                "Breakeven Upper": np.nan,
                "Breakeven Upper Percent": np.nan,
                "Max Profit": max_profit,
                "Max Loss": spread_cost[0] * -1,
            }
        )

        call_spread = pd.DataFrame(
            data=call_spread_.values(), index=call_spread_.keys()
        ).rename(columns={0: "Bull Call Spread"})
        if call_spread.loc["Cost"][0] < 0:
            call_spread.loc["Max Profit"][0] = call_spread.loc["Cost"][0] * -1
            call_spread.loc["Max Loss"][0] = -1 * (
                bought - sold + call_spread.loc["Cost"][0]
            )
            lower = bought if sold > bought else sold
            call_spread.loc["Breakeven Upper"][0] = (
                lower + call_spread.loc["Max Profit"][0]
            )
            call_spread.loc["Breakeven Upper Percent"][0] = round(
                (breakeven_price / options.last_price * 100) - 100, ndigits=4
            )
            call_spread.loc["Breakeven Lower"][0] = np.nan
            call_spread.loc["Breakeven Lower Percent"][0] = np.nan
            call_spread.rename(
                columns={"Bull Call Spread": "Bear Call Spread"}, inplace=True
            )

        call_spread.loc["Payoff Ratio"] = round(
            abs(call_spread.loc["Max Profit"][0] / call_spread.loc["Max Loss"][0]),
            ndigits=4,
        )

        return call_spread
    return pd.DataFrame()


def calculate_vertical_put_spread(
    options: Options,
    days: Optional[int] = 30,
    sold_strike: Optional[float] = 0,
    bought_strike: Optional[float] = 0,
) -> pd.DataFrame:
    """Calculates the vertical put spread for the target DTE.
    A bear put spread is when the bought strike is above the sold strike.

    Parameters
    ----------
    options : object
        The Options data object. Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry. This value will be used to get the nearest valid DTE.
        Default is 30 days.
    sold_strike: float
        The target strike price for the short leg of the vertical put spread. Default is the last price of the underlying.
    bought_strike: float
        The target strike price for the long leg of the vertical put spread.
        Default is the 5% OTM above the last price of the underlying.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results. Strike 1 is the sold strike, strike 2 is the bought strike.

    Examples
    --------
    Load the data:
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains()
    >>> data = OptionsChains("QQQ")

    For a bull put spread:
    >>> data.get_vertical_put_spread(data, days=10, sold_strike=355, bought_strike=350)

    For a bear put spread:
    >>> data.get_vertical_put_spread(data, days=10, sold_strike=355, bought_strike=350)
    """
    options = deepcopy(options)

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if not days:
        days = 30

    if not bought_strike:
        bought_strike = options.last_price * 0.9750

    if not sold_strike:
        sold_strike = options.last_price * 0.9250

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841
    options = validate_object(options, "nonZeroPrices", dte_estimate)
    sold = get_nearest_put_strike(options, days, sold_strike)
    bought = get_nearest_put_strike(options, days, bought_strike)

    sold_premium = options.chains.query(
        "`strike` == @sold and `dte` == @dte_estimate and `optionType` == 'put'"
    )["bid"].values * (-1)
    bought_premium = options.chains.query(
        "`strike` == @bought and `dte` == @dte_estimate and `optionType` == 'put'"
    )["ask"].values

    spread_cost = bought_premium + sold_premium
    max_profit = abs(spread_cost[0])
    breakeven_price = sold - max_profit
    max_loss = (sold - bought - max_profit) * -1
    put_spread_: dict[str, Any] = {}
    if sold != bought and max_loss != 0:
        # Includees the as-of date if it is historical EOD data.
        if (
            options.source == "Intrinio"
            and options.date != ""
            or options.source == "TMX"
            and options.date != ""
        ):
            put_spread_.update({"Date": options.date})

        put_spread_.update(
            {
                "Symbol": options.symbol,
                "Underlying Price": options.last_price,
                "Expiration": options.chains.query("`dte` == @dte_estimate")[
                    "expiration"
                ].unique()[0],
                "DTE": dte_estimate,
                "Strike 1": sold,
                "Strike 2": bought,
                "Strike 1 Premium": sold_premium[0],
                "Strike 2 Premium": bought_premium[0],
                "Cost": spread_cost[0],
                "Cost Percent": round(max_profit / options.last_price * 100, ndigits=4),
                "Breakeven Lower": np.nan,
                "Breakeven Lower Percent": np.nan,
                "Breakeven Upper": breakeven_price,
                "Breakeven Upper Percent": (
                    100 - round((breakeven_price / options.last_price) * 100, ndigits=4)
                ),
                "Max Profit": max_profit,
                "Max Loss": max_loss,
            }
        )

        put_spread = pd.DataFrame(
            data=put_spread_.values(), index=put_spread_.keys()
        ).rename(columns={0: "Bull Put Spread"})
        if put_spread.loc["Cost"][0] > 0:
            put_spread.loc["Max Profit"][0] = bought - sold - spread_cost[0]
            put_spread.loc["Max Loss"][0] = spread_cost[0] * (-1)
            put_spread.loc["Breakeven Lower"][0] = bought - spread_cost[0]
            put_spread.loc["Breakeven Lower Percent"][0] = 100 - round(
                (breakeven_price / options.last_price) * 100, ndigits=4
            )
            put_spread.loc["Breakeven Upper"][0] = np.nan
            put_spread.loc["Breakeven Upper Percent"][0] = np.nan
            put_spread.rename(
                columns={"Bull Put Spread": "Bear Put Spread"}, inplace=True
            )

        put_spread.loc["Payoff Ratio"] = round(
            abs(put_spread.loc["Max Profit"][0] / put_spread.loc["Max Loss"][0]),
            ndigits=4,
        )

        return put_spread
    return pd.DataFrame()


def calculate_synthetic_long(
    options: Options,
    days: Optional[int] = 30,
    strike: float = 0,
) -> pd.DataFrame:
    """Calculates the cost of a synthetic long position at a given strike.
    It is expressed as the difference between a bought call and a sold put.
    Requires the Options data object.

    Parameters
    -----------
    options : Options
        The Options data object. Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry. Default is 30 days.
    strike: float
        The target strike price. Default is the last price of the underlying stock.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results. Strike1 is the purchased call strike, strike2 is the sold put strike.

    Example
    --------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains('SPY')
    >>> options_chains_model.calculate_synthetic_long(data)
    """

    options = deepcopy(options)

    if not days:
        days = 30
    if days and days == 0:
        days = -1

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    dte_estimate = get_nearest_dte(options, days)

    options = validate_object(options, "nonZeroPrices", dte_estimate)

    strike_price = options.last_price if strike == 0 else strike

    strike_estimate = get_nearest_call_strike(options, dte_estimate, strike_price)

    call_premium = options.chains.query(
        "`strike` == @strike_estimate and `dte` == @dte_estimate and `optionType` == 'call'"
    )["ask"].values

    put_premium = options.chains.query(
        "`strike` == @strike_estimate and `dte` == @dte_estimate and `optionType` == 'put'"
    )["bid"].values * (-1)

    position_cost = call_premium[0] + put_premium[0]
    breakeven = strike_estimate + position_cost
    synthetic_long: dict[str, Any] = {}

    synthetic_long.update(
        {
            "Symbol": options.symbol,
            "Underlying Price": options.last_price,
            "Expiration": options.chains.query("`dte` == @dte_estimate")[
                "expiration"
            ].unique()[0],
            "DTE": dte_estimate,
            "Strike 1": strike_estimate,
            "Strike 2": strike_estimate,
            "Strike 1 Premium": call_premium[0],
            "Strike 2 Premium": put_premium[0],
            "Cost": position_cost,
            "Cost Percent": round(position_cost / options.last_price * 100, ndigits=4),
            "Breakeven Lower": np.nan,
            "Breakeven Lower Percent": np.nan,
            "Breakeven Upper": breakeven,
            "Breakeven Upper Percent": round(
                ((breakeven - options.last_price) / options.last_price) * 100, ndigits=4
            ),
            "Max Profit": np.inf,
            "Max Loss": breakeven * (-1),
        }
    )

    strategy = pd.DataFrame(
        data=synthetic_long.values(), index=synthetic_long.keys()
    ).rename(columns={0: "Synthetic Long"})

    return strategy


def calculate_synthetic_short(
    options: Options,
    days: Optional[int] = 30,
    strike: float = 0,
) -> pd.DataFrame:
    """Calculates the cost of a synthetic short position at a given strike.
    It is expressed as the difference between a sold call and a purchased put.
    Requires the Options data object.

    Parameters
    -----------
    options : Options
        The Options data object. Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry. Default is 30 days.
    strike: float
        The target strike price. Default is the last price of the underlying stock.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results. Strike1 is the sold call strike, strike2 is the purchased put strike.

    Example
    --------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains('SPY')
    >>> options_chains_model.calculate_synthetic_short(data)
    """

    options = deepcopy(options)

    if not days:
        days = 30
    if days and days == 0:
        days = -1

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    dte_estimate = get_nearest_dte(options, days)

    options = validate_object(options, "nonZeroPrices", dte_estimate)

    strike_price = options.last_price if strike == 0 else strike

    strike_estimate = get_nearest_call_strike(options, dte_estimate, strike_price)

    call_premium = options.chains.query(
        "`strike` == @strike_estimate and `dte` == @dte_estimate and `optionType` == 'call'"
    )["bid"].values * (-1)

    put_premium = options.chains.query(
        "`strike` == @strike_estimate and `dte` == @dte_estimate and `optionType` == 'put'"
    )["ask"].values

    position_cost = put_premium[0] + call_premium[0]
    breakeven = strike_estimate - position_cost
    synthetic_short: dict[str, Any] = {}

    synthetic_short.update(
        {
            "Symbol": options.symbol,
            "Underlying Price": options.last_price,
            "Expiration": options.chains.query("`dte` == @dte_estimate")[
                "expiration"
            ].unique()[0],
            "DTE": dte_estimate,
            "Strike 1": strike_estimate,
            "Strike 2": strike_estimate,
            "Strike 1 Premium": call_premium[0],
            "Strike 2 Premium": put_premium[0],
            "Cost": position_cost,
            "Cost Percent": round(position_cost / options.last_price * 100, ndigits=4),
            "Breakeven Lower": breakeven,
            "Breakeven Lower Percent": round(
                ((breakeven - options.last_price) / options.last_price) * 100, ndigits=4
            ),
            "Breakeven Upper": np.nan,
            "Breakeven Upper Percent": np.nan,
            "Max Profit": breakeven,
            "Max Loss": np.inf,
        }
    )

    strategy = pd.DataFrame(
        data=synthetic_short.values(), index=synthetic_short.keys()
    ).rename(columns={0: "Synthetic Short"})

    return strategy


@log_start_end(log=logger)
def calculate_stats(options: Options, by: Optional[str] = "expiration") -> pd.DataFrame:
    """Calculates basic statistics for the options chains, like OI and Vol/OI ratios.

    Parameters
    ----------
    options : object
        The Options data object.
        Accepts both Pydantic and Pandas object types, as defined by `load_options_chains()`.
        A Pandas DataFrame, or dictionary, with the options chains data is also accepted.
    by: str
        Whether to calculate by strike or expiration.  Default is expiration.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the calculated statistics.

    Examples
    --------
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
    >>> data = OptionsChains("SPY")

    By expiration date:
    >>> data.calculate_stats()

    By strike:
    >>> data.calculate_stats(data, "strike")
    """

    if by not in ["expiration", "strike"]:
        console.print(
            "Invalid choice.  The supported methods are: [expiration, strike]"
        )
        return pd.DataFrame()

    chains = deepcopy(options)
    last_price = chains.last_price if hasattr(chains, "last_price") else None
    chains = validate_object(chains, scope="chains")

    if chains.empty or chains is None:
        return chains == pd.DataFrame()

    stats = pd.DataFrame()

    stats["Puts OI"] = (
        chains[chains["optionType"] == "put"]
        .groupby(f"{by}")[["openInterest"]]
        .sum(numeric_only=True)
        .astype("int64")
    )
    stats["Calls OI"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{by}")[["openInterest"]]
        .sum(numeric_only=True)
        .astype("int64")
    )
    stats["Total OI"] = stats["Calls OI"] + stats["Puts OI"]
    stats["OI Ratio"] = round(stats["Puts OI"] / stats["Calls OI"], 2)

    if by == "expiration" and last_price:
        stats["Puts OTM"] = (
            chains.query("`optionType` == 'put' & `strike` < @last_price")
            .groupby("expiration")[["openInterest"]]
            .sum(numeric_only=True)
        )
        stats["Calls OTM"] = (
            chains.query("`optionType` == 'call' & `strike` > @last_price")
            .groupby("expiration")[["openInterest"]]
            .sum(numeric_only=True)
        )
        stats["Puts ITM"] = (
            chains.query("`optionType` == 'put' & `strike` > @last_price")
            .groupby("expiration")[["openInterest"]]
            .sum(numeric_only=True)
        )
        stats["Calls ITM"] = (
            chains.query("`optionType` == 'call' & `strike` < @last_price")
            .groupby("expiration")[["openInterest"]]
            .sum(numeric_only=True)
        )
        stats["OTM Ratio"] = round(stats["Puts OTM"] / stats["Calls OTM"], 2)
        stats["ITM Percent"] = round(
            (stats["Puts ITM"] + stats["Calls ITM"]) / stats["Total OI"] * 100, 2
        )

    stats["Puts Volume"] = (
        chains[chains["optionType"] == "put"]
        .groupby(f"{by}")[["volume"]]
        .sum(numeric_only=True)
        .astype("int64")
    )
    stats["Calls Volume"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{by}")
        .sum(numeric_only=True)[["volume"]]
        .astype("int64")
    )
    stats["Total Volume"] = stats["Calls Volume"] + stats["Puts Volume"]
    stats["Volume Ratio"] = round(stats["Puts Volume"] / stats["Calls Volume"], 2)
    stats["Vol-OI Ratio"] = round(stats["Total Volume"] / stats["Total OI"], 2)
    stats.rename_axis("Expiration", inplace=True)
    if by == "strike":
        stats.rename_axis(index={"Expiration": "Strike"}, inplace=True)
    return stats.replace([np.nan, np.inf], None)


@log_start_end(log=logger)
def get_strategies(
    options: Options,
    days: Optional[list[int]] = None,
    straddle_strike: Optional[float] = 0,
    strangle_moneyness: Optional[list[float]] = None,
    synthetic_longs: Optional[list[float]] = None,
    synthetic_shorts: Optional[list[float]] = None,
    vertical_calls: Optional[list[float]] = None,
    vertical_puts: Optional[list[float]] = None,
) -> pd.DataFrame:
    """Gets options strategies for all, or a list of, DTE(s).
    Currently supports straddles, strangles, and vertical spreads.
    Multiple strategies, expirations, and % moneyness can be returned.
    A negative value for `straddle_strike` or `strangle_moneyness` returns short options.
    A synthetic long/short position is a bought/sold call and sold/bought put at the same strike.
    A sold call strike that is lower than the bought strike, or a sold put strike that is higher than the bought strike,
    is a bearish vertical spread.

    Parameters
    ----------
    options: object
        The Options data object. Use `load_options_chains()` to load the data.
    days: list[int]
        List of DTE(s) to get strategies for. Enter a single value, or multiple as a list. Defaults to all.
    strike_price: float
        The target strike price. Defaults to the last price of the underlying stock.
    strangle_moneyness: list[float]
        List of OTM moneyness to target, expressed as a percent value between 0 and 100.
        Enter a single value, or multiple as a list. Defaults to 5.
    synthetic_long: list[float]
        List of strikes for a synthetic long position.
    synthetic_short: list[float]
        List of strikes for a synthetic short position.
    vertical_calls: list[float]
        Call strikes for vertical spreads, listed as [sold strike, bought strike].
    vertical_puts: list[float]
        Put strikes for vertical spreads, listed as [sold strike, bought strike].
    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.

    Examples
    --------
    Load data
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.load_options_chains("SPY")

    Return just straddles
    >>> options_chains_model.calculate_strategies(data)

    Return strangles
    >>> options_chains_model.calculate_strategies(data, strangle_moneyness = 10)

    Return multiple values for both moneness and days:
    >>> options_chains_model.calculate_strategies(data, days = [10,30,60,90], moneyness = [2.5,-5,10,-20])

    Return vertical spreads for all expirations.
    >>> options_chains_model.calculate_strategies(data, vertical_calls=[430,427], vertical_puts=[420,426])

    Return synthetic short and long positions:
    >>> options_chains_model.calculate_strategies(
        data, days = [30,60], synthetic_short = [450,445], synthetic_long = [450,455]
    )
    """

    def to_clean_list(x):
        if x is None:
            return None
        return [x] if not isinstance(x, list) else x

    options = deepcopy(options)

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        console.print("`last_price` was not found in the Options data object.")
        return pd.DataFrame()

    options.chains = (
        pd.DataFrame(options.chains)
        if isinstance(options.chains, dict)
        else options.chains
    )

    strangle_moneyness = strangle_moneyness or [0.0]
    days = days or options.chains["dte"].unique().tolist()

    # Allows a single input to be passed instead of a list.
    days = [days] if isinstance(days, int) else days  # type: ignore[list-item]

    if not isinstance(vertical_calls, (list, float)) and vertical_calls is not None:
        console.print(
            "Two strike prices are required. Enter the sold price first, then the bought price."
        )
        return pd.DataFrame()
    if not isinstance(vertical_puts, (list, float)) and vertical_puts is not None:
        console.print(
            "Two strike prices are required. Enter the sold price first, then the bought price."
        )
        return pd.DataFrame()

    strangle_moneyness = to_clean_list(strangle_moneyness)
    synthetic_longs = to_clean_list(synthetic_longs)
    synthetic_shorts = to_clean_list(synthetic_shorts)

    days_list = []
    strategies = pd.DataFrame()
    straddles = pd.DataFrame()
    strangles = pd.DataFrame()
    strangles_ = pd.DataFrame()
    synthetic_longs_df = pd.DataFrame()
    _synthetic_longs = pd.DataFrame()
    synthetic_shorts_df = pd.DataFrame()
    _synthetic_shorts = pd.DataFrame()
    call_spreads = pd.DataFrame()
    put_spreads = pd.DataFrame()

    for day in days:
        day = day or -1  # noqa: PLW2901
        days_list.append(get_nearest_dte(options, day))
    days = list(set(days_list))
    days.sort()

    if vertical_calls is not None:
        cStrike1 = vertical_calls[0]
        cStrike2 = vertical_calls[1]
        for day in days:
            call_spread = calculate_vertical_call_spread(
                options, day, cStrike1, cStrike2
            ).transpose()
            call_spreads = pd.concat([call_spreads, call_spread])

    if vertical_puts:
        pStrike1 = vertical_puts[0]
        pStrike2 = vertical_puts[1]
        for day in days:
            put_spread = calculate_vertical_put_spread(
                options, day, pStrike1, pStrike2
            ).transpose()
            put_spreads = pd.concat([put_spreads, put_spread])

    if straddle_strike:
        straddle_strike = (
            options.last_price if straddle_strike == 0 else straddle_strike
        )
        for day in days:
            straddle = calculate_straddle(options, day, straddle_strike).transpose()
            if straddle.iloc[0]["Cost"] != 0:
                straddles = pd.concat([straddles, straddle])

    if strangle_moneyness and strangle_moneyness[0] != 0:
        for day in days:
            for moneyness in strangle_moneyness:
                strangle = calculate_strangle(options, day, moneyness).transpose()
                if strangle.iloc[0]["Cost"] != 0:
                    strangles_ = pd.concat([strangles_, strangle])

        strangles = pd.concat([strangles, strangles_])
        strangles = strangles.query("`Strike 1` != `Strike 2`").drop_duplicates()

    if synthetic_longs:
        strikes = synthetic_longs
        for day in days:
            for strike in strikes:
                _synthetic_long = calculate_synthetic_long(
                    options, day, strike
                ).transpose()
                if _synthetic_long.iloc[0]["Strike 1 Premium"] != 0:
                    _synthetic_longs = pd.concat([_synthetic_longs, _synthetic_long])

        synthetic_longs_df = pd.concat([synthetic_longs_df, _synthetic_longs])

    if synthetic_shorts:
        strikes = synthetic_shorts
        for day in days:
            for strike in strikes:
                _synthetic_short = calculate_synthetic_short(
                    options, day, strike
                ).transpose()
                if _synthetic_short.iloc[0]["Strike 1 Premium"] != 0:
                    _synthetic_shorts = pd.concat([_synthetic_shorts, _synthetic_short])

        synthetic_shorts_df = pd.concat([synthetic_shorts_df, _synthetic_shorts])

    strategies = pd.concat(
        [
            straddles,
            strangles,
            synthetic_longs_df,
            synthetic_shorts_df,
            call_spreads,
            put_spreads,
        ]
    )

    if strategies.empty:
        return get_strategies(options, straddle_strike=options.last_price)

    strategies = strategies.reset_index().rename(columns={"index": "Strategy"})
    strategies = (
        strategies.set_index(["Expiration", "DTE"])
        .sort_index()
        .drop(columns=["Symbol"])
    )
    return strategies.reset_index()


@log_start_end(log=logger)
def calculate_skew(
    options, expiration: Optional[str] = "", moneyness: Optional[float] = None
) -> pd.DataFrame:
    """
    Returns the skewness of the options, either vertical or horizontal.

    The vertical skew for each expiry and option is calculated by subtracting the IV of the ATM call or put.
    Returns only where the IV is greater than 0.

    Horizontal skew is returned if a value for moneyness is supplied.
    It is expressed as the difference between skews of two equidistant OTM strikes (the closest call and put).

    Parameters
    -----------
    options: object
        The Options data object. Use `load_options_chains()` to load the data.
    expiration: str
        The expiration date to target.  Defaults to all.
    moneyness: float
        The moneyness to target for calculating horizontal skew.  This parameter overrides a defined expiration date.

    Returns
    --------
    pd.DataFrame
        Pandas DataFrame with the results.

    Examples
    ----------
    >>> from openbb_terminal.stocks.options import options_chains_model as op
    >>> data = op.load_options_chains("SPY")

    Vertical skew at a given expiry:
    >>> skew = op.calculate_skew(data, "2025-12-19")

    Vertical skew at all expirations:
    >>> skew = op.calculate_skew(data)

    Horizontal skew at a given % OTM:
    >>> skew = op.calculate_skew(data, moneyness = 10)
    """

    options = deepcopy(options)

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if options.hasIV is False:
        console.print(
            "Options data object does not have Implied Volatility and is required for this function."
        )
        return pd.DataFrame()

    options.chains = validate_object(options.chains, scope="chains")
    options.chains = options.chains[options.chains["impliedVolatility"] > 0]
    days = options.chains["dte"].unique().tolist()
    # expiration = get_nearest_expiration(options, expiration)
    if moneyness is not None:
        calls = pd.DataFrame()
        atm_call_iv = pd.DataFrame()
        puts = pd.DataFrame()
        atm_put_iv = pd.DataFrame()
        skew_df = pd.DataFrame()
        strikes = get_nearest_otm_strike(options, moneyness)
        for day in days:
            atm_call_strike = get_nearest_call_strike(  # noqa:F841
                options, day, options.last_price
            )
            call_strike = get_nearest_call_strike(  # noqa:F841
                options, day, strikes["call"]
            )
            if (
                len(
                    options.chains[options.chains["dte"] == day].query(
                        "`optionType` == 'call'"
                    )
                )
                > 0
            ):
                call_iv = options.chains[options.chains["dte"] == day].query(
                    "`optionType` == 'call' & `strike` == @call_strike"
                )[["expiration", "strike", "impliedVolatility"]]
                calls = pd.concat([calls, call_iv])
                atm_call = options.chains[options.chains["dte"] == day].query(
                    "`optionType` == 'call' & `strike` == @atm_call_strike"
                )[["expiration", "strike", "impliedVolatility"]]
                atm_call_iv = pd.concat([atm_call_iv, atm_call])
            atm_put_strike = get_nearest_put_strike(  # noqa:F841
                options, day, options.last_price
            )
            put_strike = get_nearest_put_strike(  # noqa:F841
                options, day, strikes["put"]
            )
            if (
                len(
                    options.chains[options.chains["dte"] == day].query(
                        "`optionType` == 'put'"
                    )
                )
                > 0
            ):
                put_iv = options.chains[options.chains["dte"] == day].query(
                    "`optionType` == 'put' & `strike` == @put_strike"
                )[["expiration", "strike", "impliedVolatility"]]
                puts = pd.concat([puts, put_iv])
                atm_put = options.chains[options.chains["dte"] == day].query(
                    "`optionType` == 'put' & `strike` == @atm_put_strike"
                )[["expiration", "strike", "impliedVolatility"]]
                atm_put_iv = pd.concat([atm_put_iv, atm_put])

        calls = calls.drop_duplicates(subset=["expiration"]).set_index("expiration")
        atm_call_iv = atm_call_iv.drop_duplicates(subset=["expiration"]).set_index(
            "expiration"
        )
        puts = puts.drop_duplicates(subset=["expiration"]).set_index("expiration")
        atm_put_iv = atm_put_iv.drop_duplicates(subset=["expiration"]).set_index(
            "expiration"
        )
        skew_df["Call Strike"] = calls["strike"]
        skew_df["Call IV"] = calls["impliedVolatility"]
        skew_df["Call ATM IV"] = atm_call_iv["impliedVolatility"]
        skew_df["Call Skew"] = skew_df["Call IV"] - skew_df["Call ATM IV"]
        skew_df["Put Strike"] = puts["strike"]
        skew_df["Put IV"] = puts["impliedVolatility"]
        skew_df["Put ATM IV"] = atm_put_iv["impliedVolatility"]
        skew_df["Put Skew"] = skew_df["Put IV"] - skew_df["Put ATM IV"]
        skew_df["ATM Skew"] = skew_df["Call ATM IV"] - skew_df["Put ATM IV"]
        skew_df["IV Skew"] = skew_df["Call Skew"] - skew_df["Put Skew"]

        return skew_df

    calls = options.chains[options.chains["optionType"] == "call"]
    puts = options.chains[options.chains["optionType"] == "put"]
    call_skew = pd.DataFrame()
    put_skew = pd.DataFrame()
    skew_df = pd.DataFrame()

    for day in days:
        atm_call_strike = get_nearest_call_strike(options, day)  # noqa:F841
        if (
            len(
                options.chains[options.chains["dte"] == day].query(
                    "`optionType` == 'call'"
                )
            )
            > 0
        ):
            call = calls[calls["dte"] == day][
                ["expiration", "optionType", "strike", "impliedVolatility"]
            ]
            call = call.set_index("expiration")
            call_atm_iv = call.query("`strike` == @atm_call_strike")[
                "impliedVolatility"
            ].iloc[0]
            call["ATM IV"] = call_atm_iv
            call["Skew"] = call["impliedVolatility"] - call["ATM IV"]
            call_skew = pd.concat([call_skew, call])
        atm_put_strike = get_nearest_put_strike(options, day)  # noqa:F841
        if (
            len(
                options.chains[options.chains["dte"] == day].query(
                    "`optionType` == 'put'"
                )
            )
            > 0
        ):
            put = puts[puts["dte"] == day][
                ["expiration", "optionType", "strike", "impliedVolatility"]
            ]
            put = put.set_index("expiration")
            put_atm_iv = put.query("`strike` == @atm_put_strike")[
                "impliedVolatility"
            ].iloc[0]
            put["ATM IV"] = put_atm_iv
            put["Skew"] = put["impliedVolatility"] - put["ATM IV"]
            put_skew = pd.concat([put_skew, put])

    call_skew = call_skew.set_index(["strike", "optionType"], append=True)
    put_skew = put_skew.set_index(["strike", "optionType"], append=True)
    skew_df = pd.concat([call_skew, put_skew]).sort_index().reset_index()
    cols = ["Expiration", "Strike", "Option Type", "IV", "ATM IV", "Skew"]
    skew_df.columns = cols
    if expiration != "":
        if expiration not in options.expirations:
            expiration = get_nearest_expiration(options, expiration)

        return skew_df.query("`Expiration` == @expiration")

    return skew_df
