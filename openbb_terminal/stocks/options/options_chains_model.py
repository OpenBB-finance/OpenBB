""" Options Chains Module """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options.cboe_model import load_options as load_cboe
from openbb_terminal.stocks.options.intrinio_model import load_options as load_intrinio
from openbb_terminal.stocks.options.nasdaq_model import load_options as load_nasdaq
from openbb_terminal.stocks.options.tmx_model import load_options as load_tmx
from openbb_terminal.stocks.options.tradier_model import load_options as load_tradier
from openbb_terminal.stocks.options.yfinance_model import load_options as load_yfinance

logger = logging.getLogger(__name__)

SOURCES = ["CBOE", "YahooFinance", "Tradier", "Intrinio", "Nasdaq", "TMX"]

# mypy: disable-error-code=attr-defined
# pylint: disable=too-many-return-statements,too-many-lines


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
    object: OptionsChains data object

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


def validate_object(options: object, scope: Optional[str] = "object") -> Any:
    """This is an internal helper function for validating the OptionsChains data object passed
    through the input of functions defined in the OptionsChains class.  The purpose is to handle
    multi-type inputs with backwards compatibility and provide robust error handling.  The return
    is the portion of the object, or a true/false validation, required to perform the operation.

    Parameters
    ----------
    options : object
        The OptionsChains data object.
        Accepts both Pydantic and Pandas object types, as defined by `load_options_chains()`.
        A Pandas DataFrame, or dictionary, with the options chains data is also accepted.
    scope: str
        The scope of the data needing to be validated.  Choices are: ["chains", "object", "strategies"]

    Returns
    -------
    Any:
        if scope == "chains":
            pd.DataFrame
                Pandas DataFrame with the validated data.
        if scope == "object" or scope == "strategies":
            bool
                True if the object is a valid OptionsChains data object.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> options = options_chains_model.OptionsChains().load_options_chains("SPY")
    >>> chains = options_chains_model.validate_object(options, scope="chains")
    >>> options_chains_model.validate_object(options, scope="object")
    """

    scopes = ["chains", "object", "strategies"]

    valid: bool = True

    if scope == "":
        scope = "chains"

    if scope not in scopes:
        print("Invalid choice.  The supported methods are:", scopes)
        return pd.DataFrame()

    if scope == "object":
        try:
            if isinstance(options.strikes, list) and isinstance(
                options.expirations, list
            ):
                return valid

        except AttributeError:
            print(
                "Error: Invalid data type supplied.  The OptionsChains data object is required.  "
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

    print(
        "Error: No valid data supplied. Check the input to ensure it is not empty or None."
    )
    return not valid


def get_nearest_dte(options: object, days: Optional[int] = 30) -> int:
    """Gets the closest expiration date to the target number of days until expiry.

    Parameters
    ----------
    options : object
        The OptionsChains data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.

    Returns
    -------
    int
        The closest expiration date to the target number of days until expiry, expressed as DTE.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> options = options_chains_model.OptionsChains().load_options_chains("QQQ")
    >>> options_chains_model.get_nearest_dte(options)
    >>> options_chains_model.get_nearest_dte(options, 90)
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    nearest = (options.chains["dte"] - days).abs().idxmin()

    return options.chains.loc[nearest]["dte"]


def get_nearest_call_strike(
    options: object, days: Optional[int] = 30, strike_price: Optional[float] = 0
) -> float:
    """Gets the closest call strike to the target price and number of days until expiry.

    Parameters
    ----------
    options : object
        The OptionsChains data object.  Use load_options_chains() to load the data.
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
    >>> data = OptionsChains().load_options_chains('SPY')
    >>> get_nearest_call_strike(data)
    >>> get_nearest_call_strike(data, 90)
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

    # When Intrinio data is not EOD, there is no "ask" column, renaming "close".
    if options.source == "Intrinio" and options.date == "":
        options.chains.rename(columns={"close": "ask"}, inplace=True)

    nearest = (
        (
            options.chains[options.chains["dte"] == dte_estimate]
            .query("`optionType` == 'call' and `ask` > 0")
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
        The OptionsChains data object.  Use load_options_chains() to load the data.
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
    >>> data = OptionsChains().load_options_chains('SPY')
    >>> get_nearest_put_strike(data)
    >>> get_nearest_put_strike(data, 90)
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

    # When Intrinio data is not EOD, there is no "ask" column, renaming "close".
    if options.source == "Intrinio" and options.date == "":
        options.chains.rename(columns={"close": "ask"}, inplace=True)

    nearest = (
        (
            options.chains[options.chains["dte"] == dte_estimate]
            .query("`optionType` == 'put' and `ask` > 0")
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
        The OptionsChains data object.  Use load_options_chains() to load the data.
    moneyness: float
        The target percent OTM, expressed as a percent between 0 and 100.  Default is 5.

    Returns
    -------
    dict[str, float]
        Dictionary of the upper (call) and lower (put) strike prices.

    Example
    -------
    >>> from openbb_terminal.stocks.options import options_chains_model
    >>> data = options_chains_model.OptionsChains().load_options_chains('SPY')
    >>> strikes = options_chains_model.get_nearest_otm_strike(data)
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


@log_start_end(log=logger)
def calculate_straddle(
    options: object,
    days: Optional[int] = 30,
    strike_price: Optional[float] = 0,
    payoff: Optional[bool] = False,
) -> pd.DataFrame:
    """Calculates the cost of a straddle and its payoff profile.  Requires the OptionsChains data object.

    Parameters
    ----------
    options : object
        The OptionsChains data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.
    strike_price: float
        The target strike price.  Default is the last price of the underlying stock.
    payoff: bool
        Returns the payoff profile if True.  Default is False.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains('SPY')
    >>> openbb.stocks.options.calculate_straddle(data)
    >>> payoff = openbb.stocks.options.calculate_straddle(data, payoff = True)
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()
    if validate_object(options, scope="strategies") is False:
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    # Error handling for TMX EOD data when the date is an expiration date.  EOD, 0-day options are excluded.
    if options.source == "TMX" and options.date != "":
        options.chains = options.chains[options.chains["dte"] > 0]

    if strike_price == 0:
        strike_price = options.last_price

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841
    call_strike_estimate = get_nearest_call_strike(
        options, dte_estimate, strike_price
    )  # noqa:F841
    put_strike_estimate = get_nearest_put_strike(
        options, dte_estimate, strike_price
    )  # noqa:F841

    sT = np.arange(0, 2 * options.last_price, 1)

    def call_payoff(sT, strike_price, call_premium):
        return np.where(sT > strike_price, sT - strike_price, 0) - call_premium

    def put_payoff(sT, strike_price, put_premium):
        return np.where(sT < strike_price, strike_price - sT, 0) - put_premium

    call_premium = options.chains.query(
        "`strike` == @call_strike_estimate and `dte` == @dte_estimate and `optionType` == 'call'"
    )["ask"].values

    put_premium = options.chains.query(
        "`strike` == @put_strike_estimate and `dte` == @dte_estimate and `optionType` == 'put'"
    )["ask"].values

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
            "Call Strike": call_strike_estimate,
            "Put Strike": put_strike_estimate,
            "Call Premium": call_premium[0],
            "Put Premium": put_premium[0],
            "Cost": straddle_cost[0],
            "Cost Percent": round(
                straddle_cost[0] / options.last_price * 100, ndigits=4
            ),
            "Breakeven Upper": call_strike_estimate + straddle_cost[0],
            "Breakeven Lower": put_strike_estimate - straddle_cost[0],
        }
    )

    straddle = pd.DataFrame(data=straddle.values(), index=straddle.keys()).rename(
        columns={0: "Straddle"}
    )

    if payoff is False:
        return straddle

    payoff_call = call_payoff(sT, call_strike_estimate, call_premium)
    payoff_put = put_payoff(sT, put_strike_estimate, put_premium)
    payoff_straddle = payoff_call + payoff_put
    payoff_df = pd.DataFrame()
    payoff_df["Price at Expiration"] = sT
    payoff_df["Long Call Payoff"] = payoff_call
    payoff_df["Long Put Payoff"] = payoff_put
    payoff_df["Long Straddle Payoff"] = payoff_straddle
    payoff_df = payoff_df.set_index("Price at Expiration")

    return payoff_df


@log_start_end(log=logger)
def calculate_strangle(
    options: object,
    days: Optional[int] = 30,
    moneyness: float = 5,
    payoff: Optional[bool] = False,
) -> pd.DataFrame:
    """Calculates the cost of a straddle and its payoff profile.  Requires the OptionsChains data object.

    Parameters
    ----------
    options : object
        The OptionsChains data object.  Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry.  Default is 30 days.
    moneyness: float
        The percentage of OTM moneyness, expressed as a percent between 0 and 100.  Default is 5.
    payoff: bool
        Returns the payoff profile if True.  Default is False.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results, the payoff profile if payoff is True.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains('SPY')
    >>> openbb.stocks.options.calculate_strangle(data)
    >>> payoff = openbb.stocks.options.calculate_strangle(data, days = 10, moneyness = 0.5, payoff = True)
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    # Error handling for TMX EOD data when the date is an expiration date.  EOD, 0-day options are excluded.
    if options.source == "TMX" and options.date != "":
        options.chains = options.chains[options.chains["dte"] > 0]

    if moneyness > 100 or moneyness < 0:
        print("Error: Moneyness must be between 0 and 100.")
        return pd.DataFrame()

    strikes = get_nearest_otm_strike(options, moneyness)

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841
    call_strike_estimate = get_nearest_call_strike(
        options, dte_estimate, strikes["call"]
    )  # noqa:F841
    put_strike_estimate = get_nearest_put_strike(
        options, dte_estimate, strikes["put"]
    )  # noqa:F841

    sT = np.arange(0, 2 * options.last_price, 1)

    def call_payoff(sT, strike_price, call_premium):
        return np.where(sT > strike_price, sT - strike_price, 0) - call_premium

    def put_payoff(sT, strike_price, put_premium):
        return np.where(sT < strike_price, strike_price - sT, 0) - put_premium

    call_premium = options.chains.query(
        "`strike` == @call_strike_estimate and `dte` == @dte_estimate and `optionType` == 'call'"
    )["ask"].values

    put_premium = options.chains.query(
        "`strike` == @put_strike_estimate and `dte` == @dte_estimate and `optionType` == 'put'"
    )["ask"].values

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
            "Call Strike": call_strike_estimate,
            "Put Strike": put_strike_estimate,
            "Call Premium": call_premium[0],
            "Put Premium": put_premium[0],
            "Cost": strangle_cost[0],
            "Cost Percent": round(
                strangle_cost[0] / options.last_price * 100, ndigits=4
            ),
            "Breakeven Upper": call_strike_estimate + strangle_cost[0],
            "Breakeven Lower": put_strike_estimate - strangle_cost[0],
        }
    )

    strangle = pd.DataFrame(data=strangle.values(), index=strangle.keys()).rename(
        columns={0: "Strangle"}
    )

    if payoff is False:
        return strangle

    payoff_call = call_payoff(sT, call_strike_estimate, call_premium)
    payoff_put = put_payoff(sT, put_strike_estimate, put_premium)
    payoff_straddle = payoff_call + payoff_put
    payoff_df = pd.DataFrame()
    payoff_df["Price at Expiration"] = sT
    payoff_df["Long Call Payoff"] = payoff_call
    payoff_df["Long Put Payoff"] = payoff_put
    payoff_df["Long Strangle Payoff"] = payoff_straddle
    payoff_df = payoff_df.set_index("Price at Expiration")

    return payoff_df


def calculate_vertical_call_spread(
    options: object,
    days: int = 30,
    sold_strike: float = 0,
    bought_strike: float = 0,
) -> pd.DataFrame:
    """Calculates the vertical call spread for the target DTE.

    Parameters
    ----------
    options : object
        The OptionsChains data object. Use load_options_chains() to load the data.
    days: int
        The target number of days until expiry. This value will be used to get the nearest valid DTE.
        Default is 30 days.
    sold_strike: float
        The target strike price for the short leg of the vertical call spread.
    bought_strike: float
        The target strike price for the long leg of the vertical call spread.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.

    Examples
    --------
    Load the data:
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains()
    >>> op = OptionsChains()
    >>> data = op.load_options_chains("QQQ")

    For a bull call spread:
    >>> op.calculate_vertical_call_spread(data, days=10, sold_strike=355, bought_strike=350)

    For a bear call spread:
    >>> op.calculate_vertical_call_spread(data, days=10, sold_strike=350, bought_strike=355)
    """

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    # Error handling for TMX EOD data when the date is an expiration date.  EOD, 0-day options are excluded.
    if options.source == "TMX" and options.date != "":
        options.chains = options.chains[options.chains["dte"] > 0]

    dte_estimate = get_nearest_dte(options, days)  # noqa:F841

    sold = get_nearest_call_strike(options, days, sold_strike)
    bought = get_nearest_call_strike(options, days, bought_strike)

    # When the source is Intrinio and it is not EOD data, there is no bid/ask column.  Substituting "close".
    if options.source == "Intrinio" and options.date == "":
        sold_premium = options.chains.query(
            "`strike` == @sold and `dte` == @dte_estimate and `optionType` == 'call'"
        )["close"].values
        bought_premium = options.chains.query(
            "`strike` == @bought and `dte` == @dte_estimate and `optionType` == 'call'"
        )["close"].values
    else:
        sold_premium = options.chains.query(
            "`strike` == @sold and `dte` == @dte_estimate and `optionType` == 'call'"
        )["bid"].values
        bought_premium = options.chains.query(
            "`strike` == @bought and `dte` == @dte_estimate and `optionType` == 'call'"
        )["ask"].values

    spread_cost = bought_premium - sold_premium
    breakeven_price = bought + spread_cost[0]
    max_profit = sold - bought - spread_cost[0]
    call_spread = {}

    # Includees the as-of date if it is historical EOD data.
    if (
        options.source == "Intrinio"
        and options.date != ""
        or options.source == "TMX"
        and options.date != ""
    ):
        call_spread.update({"Date": options.date})

    call_spread.update(
        {
            "Symbol": options.symbol,
            "Underlying Price": options.last_price,
            "Expiration": options.chains.query("`dte` == @dte_estimate")[
                "expiration"
            ].unique()[0],
            "DTE": dte_estimate,
            "Sold Strike": sold,
            "Bought Strike": bought,
            "Sold Strike Premium": sold_premium[0],
            "Bought Strike Premium": bought_premium[0],
            "Cost": spread_cost[0],
            "Cost Percent": round(spread_cost[0] / options.last_price * 100, ndigits=4),
            "Breakeven": breakeven_price,
            "Breakeven Percent": round(
                (breakeven_price / options.last_price * 100) - 100, ndigits=4
            ),
            "Max Profit": max_profit,
            "Max Loss": spread_cost[0] * -1,
        }
    )

    call_spread = pd.DataFrame(
        data=call_spread.values(), index=call_spread.keys()
    ).rename(columns={0: "Bull Call Spread"})
    if call_spread.loc["Cost"][0] < 0:
        call_spread.loc["Max Profit"][0] = call_spread.loc["Cost"][0] * -1
        call_spread.loc["Max Loss"][0] = -1 * (
            bought - sold + call_spread.loc["Cost"][0]
        )
        lower = bought if sold > bought else sold
        call_spread.loc["Breakeven"][0] = lower + call_spread.loc["Max Profit"][0]
        call_spread.rename(
            columns={"Bull Call Spread": "Bear Call Spread"}, inplace=True
        )

    call_spread.loc["Payoff Ratio"] = round(
        abs(call_spread.loc["Max Profit"][0] / call_spread.loc["Max Loss"][0]),
        ndigits=4,
    )

    return call_spread


@log_start_end(log=logger)
def calculate_stats(options: object, by: Optional[str] = "expiration") -> pd.DataFrame:
    """Calculates basic statistics for the options chains, like OI and Vol/OI ratios.

    Parameters
    ----------
    options : object
        The OptionsChains data object.
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
    >>> data = OptionsChains().load_options_chains("SPY")
    >>> OptionsChains().calculate_stats(data)
    >>> OptionsChains().calculate_stats(data, "strike")
    >>> OptionsChains().calculate_stats(data.chains, "expiration")
    """

    if by not in ["expiration", "strike"]:
        print("Invalid choice.  The supported methods are: [expiration, strike]")
        return pd.DataFrame()

    chains = validate_object(options, scope="chains")

    if chains.empty or chains is None:
        return chains == pd.DataFrame()

    stats = pd.DataFrame()
    stats["Puts OI"] = (
        chains[chains["optionType"] == "put"]
        .groupby(f"{by}")
        .sum(numeric_only=True)[["openInterest"]]
        .astype(int)
    )
    stats["Calls OI"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{by}")
        .sum(numeric_only=True)[["openInterest"]]
        .astype(int)
    )
    stats["Total OI"] = stats["Calls OI"] + stats["Puts OI"]
    stats["OI Ratio"] = round(stats["Puts OI"] / stats["Calls OI"], 2)
    stats["Puts Volume"] = (
        chains[chains["optionType"] == "put"]
        .groupby(f"{by}")
        .sum(numeric_only=True)[["volume"]]
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

    return stats.replace([np.nan, np.inf], "")


@log_start_end(log=logger)
def get_strategies(  # pylint: disable=dangerous-default-value
    options: object,
    days: list[int] = [],
    strike_price: Optional[float] = 0,
    moneyness: list[float] = [5, 10],
    straddle: Optional[bool] = False,
    strangle: Optional[bool] = False,
) -> pd.DataFrame:
    """Gets options strategies for all, or a list of, DTE(s). Currently supports straddles and strangles.
    Multiple strategies, target strikes, or % moneyness can be returned.

    Parameters
    ----------
    options: object
        The OptionsChains data object. Use `load_options_chains()` to load the data.
    days: list[int]
        List of DTE(s) to get strategies for. Defaults to all.
    strike_price: float
        The target strike price. Defaults to the last price of the underlying stock. Only valid when straddle is True.
    moneyness: list[float]
        List of OTM moneyness to target, expressed as a percent value between 0 and 100.
        Only valid when strangle is True. Defaults to [5,10].
    straddle: bool
        Returns straddles. When all are false, defaults to be True. Multiple strategies can be returned.
    strangle: bool
        Returns strangles when True. Multiple strategies can be returned.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.

    Examples
    --------
    Load data
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
    >>> data = OptionsChains().load_options_chains("SPY")
    Return just straddles
    >>> OptionsChains().get_strategies(data)
    Return strangles
    >>> OptionsChains().get_strategies(data, strangle = True)
    Return both at 2.5, 5, 10, and 20 moneyness, and at 10,30,60, and 90 DTE.
    >>> (
            OptionsChains()
            .get_strategies(data, days = [10,30,60,90], moneyness = [2.5,5,10,20], strangle = True, straddle = True)
        )
    """

    if days == []:
        days = options.chains["dte"].unique().tolist()

    if validate_object(options, scope="object") is False:
        return pd.DataFrame()

    if validate_object(options, scope="strategies") is False:
        print("`last_price` was not found in the OptionsChain data object.")
        return pd.DataFrame()

    if isinstance(options.chains, dict):
        options.chains = pd.DataFrame(options.chains)

    if not straddle and not strangle:
        print("No strategy chosen, defaulting to straddle")
        straddle = True

    # Error handling for TMX EOD data when the date is an expiration date.  EOD, 0-day options are excluded.
    if options.source == "TMX" and options.date != "":
        options.chains = options.chains[options.chains["dte"] > 0]
    # Error handling for thin TMX data, this avoids looping errors where there are no "ask" prices.
    if options.source == "TMX" and options.date == "":
        options.chains["ask"] = options.chains["lastPrice"]

    if strike_price == 0:
        strike_price = options.last_price

    options.chains = options.chains[options.chains["ask"] > 0]

    days_list = []

    strategies = pd.DataFrame()
    straddles = pd.DataFrame()
    strangles = pd.DataFrame()
    strangles_ = pd.DataFrame()

    for day in days:
        days_list.append(get_nearest_dte(options, day))
    days = list(set(days_list))
    if straddle:
        for day in days:
            straddles = pd.concat(
                [straddles, calculate_straddle(options, day, strike_price).transpose()]
            )

    if strangle:
        for day in days:
            for moneynes in moneyness:
                strangles_ = pd.concat(
                    [strangles_, calculate_strangle(options, day, moneynes).transpose()]
                )
        strangles = pd.concat([strangles, strangles_])
        strangles = strangles.query("`Call Strike` != `Put Strike`").drop_duplicates()

    strategies = pd.concat([straddles, strangles])

    strategies = strategies.reset_index().rename(columns={"index": "Strategy"})
    strategies = (
        strategies.set_index(["Expiration", "Strategy", "DTE"])
        .sort_index()
        .drop(columns=["Symbol"])
    )

    return strategies.reset_index(["Strategy", "DTE"])


class OptionsChains:  # pylint: disable=too-few-public-methods
    """OptionsChains class for loading and interacting with the OptionsChains data object.
    Use `load_options_chains()` to load the data to a variable and then feed the object to
    the input of the other functions.

    Attributes
    ----------
    load_options_chains: Callable
        Function for loading the OptionsChains data object for all data sources.
    calculate_stats: Callable
        Function to return a table of summary statistics, by strike or by expiration.
    calculate_straddle: Callable
        Function to calculate straddles and generate an optional table with the payoff profile.
    calculate_strangle: Callable
        Function to calculate strangles and generate an optional table with the payoff profile.
    get_strategies: Callable
        Function for calculating multiple straddles and strangles at different expirations and moneyness.
    """

    def __init__(self) -> None:
        self.load_options_chains: Callable = load_options_chains
        self.calculate_stats: Callable = calculate_stats
        self.calculate_vertical_call_spread: Callable = calculate_vertical_call_spread
        self.calculate_straddle: Callable = calculate_straddle
        self.calculate_strangle: Callable = calculate_strangle
        self.get_strategies: Callable = get_strategies
