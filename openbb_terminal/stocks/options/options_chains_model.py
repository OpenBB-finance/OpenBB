# pylint: disable=C0302, R0911, W0612
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
) -> object:
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
    object: Options data object

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
        print("Invalid choice. Choose from: ", list(SOURCES), sep=None)
        return None

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


def validate_object(
    options: object, scope: Optional[str] = "object", days: Optional[int] = None
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

    valid: bool = True

    if scope == "":
        scope = "chains"

    if scope not in scopes:
        print("Invalid choice.  The supported methods are:", scopes)
        return pd.DataFrame()

    if scope == "object":
        try:
            if (
                isinstance(options.strikes, list)
                and isinstance(options.expirations, list)
                and hasattr(options, "last_price")
            ):
                return valid

        except AttributeError:
            print(
                "Error: Invalid data type supplied.  The Options data object is required.  "
                "Use load_options_chains() first."
            )
            return not valid

    if scope == "strategies":
        try:
            if isinstance(options.last_price, float):
                return valid
        except AttributeError:
            print(
                "`last_price` was not found in the OptionsChainsData object and is required for this operation."
            )
            return not valid

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
                    print(
                        "No options chains data found in the supplied object.  Use load_options_chains()."
                    )
                    return pd.DataFrame()

            if "openInterest" not in chains.columns:
                print("Expected column, openInterest, not found.")
                return pd.DataFrame()

            if "volume" not in chains.columns:
                print("Expected column, volume, not found.")
                return pd.DataFrame()
        except AttributeError:
            print("Error: Invalid data type supplied.")
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
            and options.chains.query("`dte` == @dte_estimate")["ask"].sum() == 0
        ):
            options.chains["ask"] = options.chains["lastPrice"]
        if (
            options.source == "TMX"
            or options.source == "YahooFinance"
            and options.chains.query("`dte` == @dte_estimate")["bid"].sum() == 0
        ):
            options.chains["bid"] = options.chains["lastPrice"]

        return options

    print(
        "Error: No valid data supplied. Check the input to ensure it is not empty or None."
    )

    return not valid


def get_nearest_dte(options: object, days: Optional[int] = 30) -> int:
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
    options: object, days: Optional[int] = 30, strike_price: Optional[float] = 0
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
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if strike_price == 0:
        strike_price = options.last_price

    dte_estimate = get_nearest_dte(options, days)

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
    options: object, days: Optional[int] = 30, strike_price: Optional[float] = 0
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
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if strike_price == 0:
        strike_price = options.last_price

    dte_estimate = get_nearest_dte(options, days)

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
    options: object, moneyness: Optional[float] = 5
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
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if not moneyness:
        moneyness = 5

    if 0 < moneyness < 100:
        moneyness = moneyness / 100

    if moneyness > 100 or moneyness < 0:
        print("Error: Moneyness must be expressed as a percentage between 0 and 100")
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
    options: object,
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
        print("`last_price` was not found in the OptionsChain data object.")
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

    straddle = {}

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
    options: object,
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
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841

    options = validate_object(options, "nonZeroPrices", dte_estimate)

    if moneyness > 100 or moneyness < 0:
        print("Error: Moneyness must be between 0 and 100.")
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

    strangle = {}

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
    options: object,
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
        print("`last_price` was not found in the OptionsChain data object.")
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
    )["bid"].values
    bought_premium = options.chains.query(
        "`strike` == @bought and `dte` == @dte_estimate and `optionType` == 'call'"
    )["ask"].values

    spread_cost = bought_premium - sold_premium
    breakeven_price = bought + spread_cost[0]
    max_profit = sold - bought - spread_cost[0]
    call_spread_ = {}
    if sold != bought and spread_cost != 0:
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
    options: object,
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
        print("`last_price` was not found in the OptionsChain data object.")
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
    )["bid"].values
    bought_premium = options.chains.query(
        "`strike` == @bought and `dte` == @dte_estimate and `optionType` == 'put'"
    )["ask"].values

    spread_cost = bought_premium - sold_premium
    max_profit = abs(spread_cost[0])
    breakeven_price = sold - max_profit
    max_loss = (sold - bought - max_profit) * -1
    put_spread_ = {}
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


@log_start_end(log=logger)
def calculate_stats(options: object, by: Optional[str] = "expiration") -> pd.DataFrame:
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
        print("Invalid choice.  The supported methods are: [expiration, strike]")
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
        .astype(int)
    )
    stats["Calls OI"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{by}")[["openInterest"]]
        .sum(numeric_only=True)
        .astype(int)
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
        .astype(int)
    )
    stats["Calls Volume"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{by}")
        .sum(numeric_only=True)[["volume"]]
        .astype(int)
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
    options: object,
    days: Optional[list[int]] = None,
    straddle_strike: Optional[float] = 0,
    strangle_moneyness: Optional[list[float]] = None,
    vertical_calls: Optional[list[float]] = None,
    vertical_puts: Optional[list[float]] = None,
) -> pd.DataFrame:
    """Gets options strategies for all, or a list of, DTE(s).
    Currently supports straddles, strangles, and vertical spreads.
    Multiple strategies, expirations, and % moneyness can be returned.
    To get short options, use a negative value for the `straddle_strike` price or `strangle_moneyness`.
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
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
    >>> data = OptionsChains("SPY")

    Return just straddles
    >>> data.get_strategies()

    Return strangles
    >>> data.get_strategies()

    Return multiple values for both moneness and days:
    >>> data.get_strategies(days = [10,30,60,90], moneyness = [2.5,-5,10,-20])

    Return vertical spreads for all expirations.
    >>> data.get_strategies(vertical_calls=[430,427], vertical_puts=[420,426])
    """
    options = deepcopy(options)

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        print("`last_price` was not found in the Options data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if strangle_moneyness is None:
        strangle_moneyness = [0.0]

    if days is None:
        days = options.chains["dte"].unique().tolist()

    # Allows a single input to be passed instead of a list.
    days = [days] if isinstance(days, int) else days  # type: ignore[list-item]

    if not isinstance(vertical_calls, (list, float)) and vertical_calls is not None:
        print(
            "Two strike prices are required. Enter the sold price first, then the bought price."
        )
        return pd.DataFrame()
    if not isinstance(vertical_puts, (list, float)) and vertical_puts is not None:
        print(
            "Two strike prices are required. Enter the sold price first, then the bought price."
        )
        return pd.DataFrame()

    if strangle_moneyness is not None:
        strangle_moneyness = (
            [strangle_moneyness]  # type: ignore[list-item]
            if not isinstance(strangle_moneyness, list)
            else strangle_moneyness
        )

    days_list = []

    strategies = pd.DataFrame()
    straddles = pd.DataFrame()
    strangles = pd.DataFrame()
    strangles_ = pd.DataFrame()
    call_spreads = pd.DataFrame()
    put_spreads = pd.DataFrame()

    for day in days:
        if day == 0:
            day = -1
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
                straddles = pd.concat(
                    [
                        straddles,
                        straddle,
                    ]
                )

    if strangle_moneyness and strangle_moneyness[0] != 0:
        for day in days:
            for moneyness in strangle_moneyness:
                strangle = calculate_strangle(options, day, moneyness).transpose()
                if strangle.iloc[0]["Cost"] != 0:
                    strangles_ = pd.concat(
                        [
                            strangles_,
                            strangle,
                        ]
                    )

        strangles = pd.concat([strangles, strangles_])
        strangles = strangles.query("`Strike 1` != `Strike 2`").drop_duplicates()

    strategies = pd.concat([straddles, strangles, call_spreads, put_spreads])

    if strategies.empty:
        print("No strategy was selected, returning all ATM straddles.")
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
        print(
            "Options data object does not have Implied Volatility and is required for this function."
        )
        return pd.DataFrame()

    options.chains = validate_object(options.chains, scope="chains")
    options.chains = options.chains[options.chains["impliedVolatility"] > 0]
    days = options.chains["dte"].unique().tolist()

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
            put_iv = options.chains[options.chains["dte"] == day].query(
                "`optionType` == 'put' & `strike` == @put_strike"
            )[["expiration", "strike", "impliedVolatility"]]
            puts = pd.concat([puts, put_iv])
            atm_put = options.chains[options.chains["dte"] == day].query(
                "`optionType` == 'put' & `strike` == @atm_put_strike"
            )[["expiration", "strike", "impliedVolatility"]]
            atm_put_iv = pd.concat([atm_put_iv, atm_put])

        calls = calls.set_index("expiration")
        atm_call_iv = atm_call_iv.set_index("expiration")
        puts = puts.set_index("expiration")
        atm_put_iv = atm_put_iv.set_index("expiration")
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
        put = puts[puts["dte"] == day][
            ["expiration", "optionType", "strike", "impliedVolatility"]
        ]
        put = put.set_index("expiration")
        put_atm_iv = put.query("`strike` == @atm_put_strike")["impliedVolatility"].iloc[
            0
        ]
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
            print(expiration, "is not a valid expiration.")
            return skew_df
        return skew_df.query("`Expiration` == @expiration")

    return skew_df


class OptionsChains(Options):  # pylint: disable=too-few-public-methods
    """OptionsChains class for loading and interacting with the Options data object.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load the data for.
    source: str
        The source for the data. Defaults to "CBOE". ["CBOE", "Intrinio", "Nasdaq", "TMX", "Tradier", "YahooFinance"]
    date: str
        The date for EOD chains data.  Only available for "Intrinio" and "TMX".
    pydantic: bool
        Whether to return as a Pydantic Model or as a Pandas object.  Defaults to False.

    Returns
    -------
    Object: Options
        chains: pd.DataFrame
            The complete options chain for the ticker.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: pd.Series
            The price and recent performance of the underlying asset.
        hasIV: bool
            Returns implied volatility.
        hasGreeks: bool
            Returns greeks data.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data.
        date: str
            The date, when the chains data is historical EOD.
        SYMBOLS: pd.DataFrame
            The symbol directory for the source, when available.

        Methods
        -------
        get_stats: Callable
            Function to get a table of summary statistics, by strike or by expiration.
        get_straddle: Callable
            Function to get straddles and the payoff profile.
        get_strangle: Callable
            Function to calculate strangles and the payoff profile.
        get_vertical_call_spread: Callable
            Function to get vertical call spreads.
        get_vertical_put_spreads: Callable
            Function to get vertical put spreads.
        get_strategies: Callable
            Function to get multiple straddles and strangles at different expirations and moneyness.
        get_skew: Callable
            Function to get the vertical or horizontal skewness of the options.

    Examples
    --------
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
    >>> spy = OptionsChains("SPY")
    >>> spy.__dict__

    >>> xiu = OptionsChains("xiu.to", "TMX")
    >>> xiu.get_straddle()
    """

    def __init__(self, symbol, source="CBOE", date="", pydantic=False):
        try:
            options = load_options_chains(symbol, source, date, pydantic)
            items = list(options.__dict__.keys())
            for item in items:
                setattr(self, item, options.__dict__[item])
            if hasattr(self, "date") is False:
                setattr(self, "date", "")
        except Exception:
            self.chains = pd.DataFrame()

    def __repr__(self) -> str:
        return f"OptionsChains(symbol={self.symbol}, source ={self.source})"

    def get_stats(self, by="expiration", query=None):
        """Calculates basic statistics for the options chains, like OI and Vol/OI ratios.

        Parameters
        ----------
        by: str
            Whether to calculate by strike or expiration.  Default is expiration.
        query: DataFrame
            Entry point to perform DataFrame operations on self.chains at the input stage.

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

        Query:
        >>> data = OptionsChains("XIU", "TMX")
        >>> data.get_stats(query = data.chains.query("`openInterest` > 0"), by = "strike")
        """

        if query is not None:
            if isinstance(query, pd.DataFrame):
                return calculate_stats(query, by)
            print("Query must be passed a Pandas DataFrame with chains data.")

        return calculate_stats(self, by)

    def get_straddle(self, days=0, strike=0):
        """Calculates the cost of a straddle and its payoff profile. Use a negative strike price for short options.
        Requires the Options data object.

        Parameters
        ----------
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
        >>> data.get_straddle()
        """

        return calculate_straddle(self, days, strike)

    def get_strangle(self, days=0, moneyness=0):
        """Calculates the cost of a strangle and its payoff profile.
        Use a negative value for moneyness for short options.

        Requires the Options data object.

        Parameters
        ----------
        days: int
            The target number of days until expiry.  Default is 30 days.
        moneyness: float
            The percentage of OTM moneyness, expressed as a percent between -100 < 0 < 100.
            Enter a negative number for short options.
            Default is 5.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results.
            Strike 1 is the nearest call strike, and strike 2 is the nearest put strike.

        Examples
        --------
        >>> data = openbb.stocks.options.load_options_chains("SPY")
        >>> data.get_strangle()
        """

        return calculate_strangle(self, days, moneyness)

    def get_vertical_call_spread(self, days=0, sold_strike=0, bought_strike=0):
        """Calculates the vertical call spread for the target DTE.
        A bull call spread is when the sold strike is above the bought strike.

        Parameters
        ----------
        days: int
            The target number of days until expiry. This value will be used to get the nearest valid DTE.
            Default is 30 days.
        sold_strike: float
            The target strike price for the short leg of the vertical call spread.
            Default is the 5% OTM above the last price of the underlying.
        bought_strike: float
            The target strike price for the long leg of the vertical call spread.
            Default is the last price of the underlying.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results. Strike 1 is the sold strike, and strike 2 is the bought strike.

        Examples
        --------
        Load the data:
        >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
        >>> data = OptionsChains("SPY")

        For a bull call spread:
        >>> data.get_vertical_call_spread(days=10, sold_strike=355, bought_strike=350)

        For a bear call spread:
        >>> data.get_vertical_call_spread(days=10, sold_strike=350, bought_strike=355)
        """

        return calculate_vertical_call_spread(self, days, sold_strike, bought_strike)

    def get_vertical_put_spread(self, days=0, sold_strike=0, bought_strike=0):
        """Calculates the vertical put spread for the target DTE.
        A bear put spread is when the bought strike is above the sold strike.

        Parameters
        ----------
        days: int
            The target number of days until expiry. This value will be used to get the nearest valid DTE.
            Default is 30 days.
        sold_strike: float
            The target strike price for the short leg of the vertical put spread.
            Default is the last price of the underlying.
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
        >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
        >>> data = OptionsChains("QQQ")

        For a bull put spread:
        >>> data.get_vertical_put_spread(days=10, sold_strike=355, bought_strike=350)

        For a bear put spread:
        >>> data.get_vertical_put_spread(days=10, sold_strike=355, bought_strike=350)
        """

        return calculate_vertical_put_spread(self, days, sold_strike, bought_strike)

    def get_strategies(
        self,
        days: Optional[list[int]] = None,
        straddle_strike: Optional[float] = None,
        strangle_moneyness: Optional[float] = None,
        vertical_calls: Optional[list[float]] = None,
        vertical_puts: Optional[list[float]] = None,
    ):
        """Gets options strategies for all, or a list of, DTE(s).
        Currently supports straddles, strangles, and vertical spreads.
        Multiple strategies, expirations, and % moneyness can be returned.
        To get short options, use a negative value for the `straddle_strike` price or `strangle_moneyness`.
        A sold call strike that is lower than the bought strike,
        and a sold put strike that is higher than the bought strike,
        are both bearish.

        Parameters
        ----------
        days: list[int]
            List of DTE(s) to get strategies for. Enter a single value, or multiple as a list. Defaults to all.
            This is the only shared parameter across strategies.
        strike_price: float
            The target strike price for straddles. Defaults to the last price of the underlying stock.
            Enter a negative value for short straddles.
        strangle_moneyness: list[float]
            List of OTM moneyness to target, expressed as a percent value between 0 and 100.
            Enter a single value, or multiple as a list. Defaults to 5. Enter a negative value for short straddles.
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
        >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
        >>> data = OptionsChains("SPY")

        Return just long straddles for every expiry.
        >>> data.get_strategies()

        Return strangles for every expiry.
        >>> data.get_strategies(strangle_moneyness = [2.5,5,10])

        Return multiple values for both moneness and days:
        >>> data.get_strategies(days = [10,30,60,90], moneyness = [2.5,-5,10,-20])

        Return vertical spreads for all expirations.
        >>> data.get_strategies(vertical_calls=[430,427], vertical_puts=[420,426])
        """

        if strangle_moneyness is None:
            strangle_moneyness = 0

        return get_strategies(
            self,
            days,
            straddle_strike,
            strangle_moneyness,
            vertical_calls,
            vertical_puts,
        )

    def get_skew(
        self, expiration: Optional[str] = "", moneyness: Optional[float] = None
    ):
        """
        Returns the skewness of the options, either vertical or horizontal.

        The vertical skew for each expiry and option is calculated by subtracting the IV of the ATM call or put.
        Returns only where the IV is greater than 0.

        Horizontal skew is returned if a value for moneyness is supplied.
        It is expressed as the difference between skews of two equidistant OTM strikes (the closest call and put).

        Parameters
        -----------
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
        >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
        >>> data = OptionsChains("SPY")

        Vertical skew at a given expiry:
        >>> skew = data.get_skew("2025-12-19")

        Vertical skew at all expirations:
        >>> skew = data.get_skew()

        Horizontal skew at a given % OTM:
        >>> skew = data.get_skew(moneyness = 10)
        """
        return calculate_skew(self, expiration, moneyness)
