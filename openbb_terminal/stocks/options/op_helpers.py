"""Option helper functions"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from math import e, log
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel, Extra, Field
from scipy.stats import norm

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_rf
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


def get_strikes(
    min_sp: float, max_sp: float, chain: pd.DataFrame
) -> Tuple[float, float]:
    """Function to get the min and max strikes for a given expiry"""

    min_strike = chain["strike"].min() if min_sp == -1 else min_sp
    max_strike = chain["strike"].max() if max_sp == -1 else max_sp

    return min_strike, max_strike


def get_loss_at_strike(strike: float, chain: pd.DataFrame) -> float:
    """Function to get the loss at the given expiry

    Parameters
    ----------
    strike : Union[int,float]
        Value to calculate total loss at
    chain : Dataframe:
        Dataframe containing at least strike and openInterest

    Returns
    -------
    loss : Union[float,int]
        Total loss
    """

    itm_calls = chain[chain.index < strike][["OI_call"]]
    itm_calls["loss"] = (strike - itm_calls.index) * itm_calls["OI_call"]
    call_loss = itm_calls["loss"].sum()

    itm_puts = chain[chain.index > strike][["OI_put"]]
    itm_puts["loss"] = (itm_puts.index - strike) * itm_puts["OI_put"]
    put_loss = itm_puts.loss.sum()
    loss = call_loss + put_loss

    return loss


def calculate_max_pain(chain: pd.DataFrame) -> Union[int, float]:
    """Returns the max pain for a given call/put dataframe

    Parameters
    ----------
    chain : DataFrame
        Dataframe to calculate value from

    Returns
    -------
    max_pain : int
        Max pain value
    """

    strikes = np.array(chain.index)
    if ("OI_call" not in chain.columns) or ("OI_put" not in chain.columns):
        console.print("Incorrect columns.  Unable to parse max pain")
        return np.nan

    loss = [get_loss_at_strike(price_at_exp, chain) for price_at_exp in strikes]
    chain["loss"] = loss
    max_pain = chain["loss"].idxmin()

    return max_pain


def convert(orig: str, to: str) -> float:
    """Convert a string to a specific type of number
    Parameters
    ----------
    orig : str
        String to convert
    Returns
    -------
    number : float
        Decimal value of string
    """
    clean = orig.replace("%", "").replace("+", "").replace(",", "")
    if to == "%":
        return float(clean) / 100
    if to == ",":
        return float(clean)
    raise ValueError("Invalid to format, please use '%' or ','.")


def rn_payoff(x: str, df: pd.DataFrame, put: bool, delta: int, rf: float) -> float:
    """The risk neutral payoff for a stock
    Parameters
    ----------
    x : str
        Strike price
    df : pd.DataFrame
        Dataframe of stocks prices and probabilities
    put : bool
        Whether the asset is a put or a call
    delta : int
        Difference between today's date and expirations date in days
    rf : float
        The current risk-free rate

    Returns
    -------
    number : float
        Risk neutral value of option
    """
    if put:
        df["Gain"] = np.where(x > df["Price"], x - df["Price"], 0)
    else:
        df["Gain"] = np.where(x < df["Price"], df["Price"] - x, 0)
    df["Vals"] = df["Chance"] * df["Gain"]
    risk_free = (1 + rf) ** (delta / 365)
    return sum(df["Vals"]) / risk_free


@log_start_end(log=logger)
def process_option_chain(data: pd.DataFrame, source: str) -> pd.DataFrame:
    """
    Create an option chain DataFrame from the given symbol.
    Does additional processing in order to get some homogeneous between the sources.

    Parameters
    ----------
    data : pd.DataFrame
        The option chain data
    source: str, optional
        The source of the data. Valid values are "Tradier", "Nasdaq", and
        "YahooFinance". The default value is "Tradier".

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the option chain data, with columns as specified
        in the `option_chain_column_mapping` mapping, and an additional column
        "optionType" that indicates whether the option is a call or a put.
    """
    if source == "Tradier":
        df = data.rename(columns=option_chain_column_mapping["Tradier"])

    elif source == "Nasdaq":
        call_columns = ["expiration", "strike"] + [
            col for col in data.columns if col.startswith("c_")
        ]
        calls = data[call_columns].rename(columns=option_chain_column_mapping["Nasdaq"])
        calls["optionType"] = "call"

        put_columns = ["expiration", "strike"] + [
            col for col in data.columns if col.startswith("p_")
        ]
        puts = data[put_columns].rename(columns=option_chain_column_mapping["Nasdaq"])
        puts["optionType"] = "put"

        df = pd.concat([calls, puts]).drop_duplicates()

    elif source == "Intrinio":
        df = data.copy()

    elif source == "YahooFinance":
        call_columns = ["expiration", "strike"] + [
            col for col in data.columns if col.endswith("_c")
        ]
        calls = data[call_columns].rename(
            columns=option_chain_column_mapping["YahooFinance"]
        )
        calls["optionType"] = "call"

        put_columns = ["expiration", "strike"] + [
            col for col in data.columns if col.endswith("_p")
        ]
        puts = data[put_columns].rename(
            columns=option_chain_column_mapping["YahooFinance"]
        )
        puts["optionType"] = "put"

        df = pd.concat([calls, puts]).drop_duplicates()

    else:
        df = pd.DataFrame()

    return df


@log_start_end(log=logger)
def get_greeks(
    current_price: float,
    calls: pd.DataFrame,
    puts: pd.DataFrame,
    expire: str,
    div_cont: float = 0,
    rf: Optional[float] = None,
    opt_type: int = 0,
    show_all: bool = False,
    show_extra_greeks: bool = False,
) -> pd.DataFrame:
    """
    Gets the greeks for a given option

    Parameters
    ----------
    current_price: float
        The current price of the underlying
    div_cont: float
        The dividend continuous rate
    expire: str
        The date of expiration
    rf: float
        The risk-free rate
    opt_type: Union[-1, 0, 1]
        The option type 1 is for call and -1 is for put
    mini: float
        The minimum strike price to include in the table
    maxi: float
        The maximum strike price to include in the table
    show_all: bool
        Whether to show all columns from puts and calls
    show_extra_greeks: bool
        Whether to show all greeks
    """

    chain = pd.DataFrame()

    if opt_type not in [-1, 0, 1]:
        console.print("[red]Invalid option type[/red]")
    elif opt_type == 1:
        chain = calls
    elif opt_type == -1:
        chain = puts
    else:
        chain = pd.concat([calls, puts])

    chain_columns = chain.columns.tolist()
    if not all(
        col in chain_columns for col in ["strike", "impliedVolatility", "optionType"]
    ):
        if "delta" not in chain_columns:
            console.print(
                "[red]It's not possible to calculate the greeks without the following "
                "columns: `strike`, `impliedVolatility`, `optionType`.\n[/red]"
            )
        return pd.DataFrame()

    risk_free = rf if rf is not None else get_rf()
    expire_dt = datetime.strptime(expire, "%Y-%m-%d")
    dif = (expire_dt - datetime.now() + timedelta(hours=16)).total_seconds() / (
        60 * 60 * 24
    )
    strikes = []
    for _, row in chain.iterrows():
        vol = row["impliedVolatility"]
        is_call = row["optionType"] == "call"
        result = (
            [row[col] for col in row.index.tolist()]
            if show_all
            else [row[col] for col in ["strike", "impliedVolatility"]]
        )
        try:
            opt = Option(
                current_price, row["strike"], risk_free, div_cont, dif, vol, is_call
            )
            tmp = [
                opt.Delta(),
                opt.Gamma(),
                opt.Vega(),
                opt.Theta(),
            ]
            result += tmp

            if show_extra_greeks:
                result += [
                    opt.Rho(),
                    opt.Phi(),
                    opt.Charm(),
                    opt.Vanna(0.01),
                    opt.Vomma(0.01),
                ]
        except ValueError:
            result += [np.nan] * 4

            if show_extra_greeks:
                result += [np.nan] * 5
        strikes.append(result)

    greek_columns = [
        "Delta",
        "Gamma",
        "Vega",
        "Theta",
    ]
    columns = (
        chain_columns + greek_columns
        if show_all
        else ["Strike", "Implied Vol"] + greek_columns
    )

    if show_extra_greeks:
        additional_columns = ["Rho", "Phi", "Charm", "Vanna", "Vomma"]
        columns += additional_columns

    df = pd.DataFrame(strikes, columns=columns)

    return df


opt_chain_cols = {
    "lastTradeDate": {"format": "date", "label": "Last Trade Date"},
    "strike": {"format": "${x:.2f}", "label": "Strike"},
    "lastPrice": {"format": "${x:.2f}", "label": "Last Price"},
    "bid": {"format": "${x:.2f}", "label": "Bid"},
    "ask": {"format": "${x:.2f}", "label": "Ask"},
    "change": {"format": "${x:.2f}", "label": "Change"},
    "percentChange": {"format": "{x:.2f}%", "label": "Percent Change"},
    "volume": {"format": "{x:.2f}", "label": "Volume"},
    "openInterest": {"format": "", "label": "Open Interest"},
    "impliedVolatility": {"format": "{x:.2f}", "label": "Implied Volatility"},
}

option_chain_column_mapping = {
    "Nasdaq": {
        "strike": "strike",
        "c_Last": "last",
        "c_Change": "change",
        "c_Bid": "bid",
        "c_Ask": "ask",
        "c_Volume": "volume",
        "c_Openinterest": "openInterest",
        "p_Last": "last",
        "p_Change": "change",
        "p_Bid": "bid",
        "p_Ask": "ask",
        "p_Volume": "volume",
        "p_Openinterest": "openInterest",
    },
    "Tradier": {
        "open_interest": "openInterest",
        "option_type": "optionType",
    },
    "YahooFinance": {
        "contractSymbol_c": "contractSymbol",
        "lastTradeDate_c": "lastTradeDate",
        "strike": "strike",
        "lastPrice_c": "lastPrice",
        "bid_c": "bid",
        "ask_c": "ask",
        "change_c": "change",
        "percentChange_c": "percentChange",
        "volume_c": "volume",
        "openInterest_c": "openInterest",
        "impliedVolatility_c": "impliedVolatility",
        "inTheMoney_c": "inTheMoney",
        "contractSize_c": "contractSize",
        "currency_c": "currency",
        "contractSymbol_p": "contractSymbol",
        "lastTradeDate_p": "lastTradeDate",
        "lastPrice_p": "lastPrice",
        "bid_p": "bid",
        "ask_p": "ask",
        "change_p": "change",
        "percentChange_p": "percentChange",
        "volume_p": "volume",
        "openInterest_p": "openInterest",
        "impliedVolatility_p": "impliedVolatility",
        "inTheMoney_p": "inTheMoney",
        "contractSize_p": "contractSize",
        "currency_p": "currency",
        "expiration": "expiration",
    },
}


class Option:
    def __init__(
        self,
        s: float,
        k: float,
        rf: float,
        div_cont: float,
        expiry: float,
        vol: float,
        is_call: bool = True,
    ):
        """
        Class for getting the greeks of options. Inspiration from:
        http://www.smileofthales.com/computation/option-pricing-python-inheritance/

        Parameters
        ----------
        s : float
            The underlying asset price
        k : float
            The option strike price
        rf : float
            The risk-free rate
        div_cont : float
            The dividend continuous rate
        expiry : float
            The number of days until expiration
        vol : float
            The underlying volatility for an option
        is_call : bool
            True if call, False if put
        """
        if expiry <= 0:
            raise ValueError("Expiry must be greater than 0")
        if vol <= 0:
            raise ValueError("Volatility must be greater than 0")
        if s <= 0:
            raise ValueError("Price must be greater than 0")
        if k <= 0:
            raise ValueError("Strike must be greater than 0")
        self.Type = 1 if is_call else -1
        self.price = float(s)
        self.strike = float(k)
        self.risk_free = float(rf)
        self.div_cont = float(div_cont)
        self.exp_time = float(expiry) / 365.0
        self._sigma = float(vol)
        self.sigmaT = self._sigma * self.exp_time**0.5

    @property
    def d1(self):
        return (
            log(self.price / self.strike)
            + (self.risk_free - self.div_cont + 0.5 * (self.sigma**2)) * self.exp_time
        ) / self.sigmaT

    @property
    def d2(self):
        return self.d1 - self.sigmaT

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, val):
        self._sigma = val
        self.sigmaT = val * self.exp_time**0.5

    def Premium(self):
        tmpprem = self.Type * (
            self.price
            * e ** (-self.div_cont * self.exp_time)
            * norm.cdf(self.Type * self.d1)
            - self.strike
            * e ** (-self.risk_free * self.exp_time)
            * norm.cdf(self.Type * self.d2)
        )
        return tmpprem

    # 1st order greeks

    def Delta(self):
        dfq = np.exp(-self.div_cont * self.exp_time)
        if self.Type == 1:
            return dfq * norm.cdf(self.d1)
        return dfq * (norm.cdf(self.d1) - 1)

    def Vega(self):
        """Vega for 1% change in vol"""
        dfq = np.exp(-self.div_cont * self.exp_time)
        return 0.01 * self.price * dfq * norm.pdf(self.d1) * self.exp_time**0.5

    def Theta(self, time_factor=1.0 / 365.0):
        """Theta, by default for 1 calendar day change"""
        df = np.exp(-self.risk_free * self.exp_time)
        dfq = np.exp(-self.div_cont * self.exp_time)
        tmptheta = time_factor * (
            -0.5
            * self.price
            * dfq
            * norm.pdf(self.d1)
            * self.sigma
            / (self.exp_time**0.5)
            + self.Type
            * (
                self.div_cont * self.price * dfq * norm.cdf(self.Type * self.d1)
                - self.risk_free * self.strike * df * norm.cdf(self.Type * self.d2)
            )
        )
        return tmptheta

    def Rho(self):
        df = np.exp(-self.risk_free * self.exp_time)
        return (
            self.Type
            * self.strike
            * self.exp_time
            * df
            * 0.01
            * norm.cdf(self.Type * self.d2)
        )

    def Phi(self):
        dfq = np.exp(-self.div_cont * self.exp_time)
        return (
            0.01
            * -self.Type
            * self.exp_time
            * self.price
            * dfq
            * norm.cdf(self.Type * self.d1)
        )

    # 2nd order greeks

    def Gamma(self):
        dfq = np.exp(-self.div_cont * self.exp_time)
        return dfq * norm.pdf(self.d1) / (self.price * self.sigmaT)

    def Charm(self, time_factor=1.0 / 365.0):
        """Calculates Charm, by default for 1 calendar day change"""
        dfq = np.exp(-self.div_cont * self.exp_time)
        cdf = norm.cdf(self.Type * self.d1)
        return (
            time_factor
            * -dfq
            * (
                norm.pdf(self.d1)
                * (
                    (self.risk_free - self.div_cont) / (self.sigmaT)
                    - self.d2 / (2 * self.exp_time)
                )
                + (self.Type * -self.div_cont) * cdf
            )
        )

    def Vanna(self, change: float):
        """
        Vanna for a given percent change in volatility

        Parameters
        ----------
        change : float
            The change in volatility

        Returns
        ----------
        num : float
            The Vanna

        """

        return (
            change
            * -(e ** (-self.div_cont * self.exp_time))
            * self.d2
            / self.sigma
            * norm.pdf(self.d1)
        )

    def Vomma(self, change):
        """
        Vomma for a given percent change in volatility

        Parameters
        ----------
        change : float
            The change in volatility

        Returns
        ----------
        num : float
            The Vomma

        """
        return (
            change
            * np.exp(-self.div_cont * self.exp_time)
            * self.d1
            * self.d2
            * np.sqrt(self.exp_time)
            * self.price
            * norm.pdf(self.d1)
            / self._sigma
        )


def get_dte(chain: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a new column containing the DTE as an integer, including 0.
    Requires the chain to have the column labeled as, expiration.
    """
    if "expiration" not in chain.columns:
        raise ValueError("No column labeled 'expiration' was found.")

    now = datetime.now()
    temp = pd.DatetimeIndex(chain.expiration)
    temp_ = (temp - now).days + 1
    chain["dte"] = temp_

    return chain


class Options:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """The Options data object.

    Returns
    -------
    object: Options
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
    """

    chains = pd.DataFrame
    expirations: list
    strikes: list
    last_price: float
    underlying_name: str
    underlying_price: pd.Series
    hasIV: bool
    hasGreeks: bool
    symbol: str
    source: str
    date: str
    SYMBOLS: pd.DataFrame


class PydanticOptions(  # type: ignore [call-arg]
    BaseModel, extra=Extra.allow
):  # pylint: disable=too-few-public-methods

    """Pydantic model for the Options data object.

    Returns
    -------
    Pydantic: Options
        chains: dict
            The complete options chain for the ticker.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: dict
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
        SYMBOLS: dict
            The symbol directory for the source, when available.
    """

    chains: dict = Field(default=None)
    expirations: list = Field(default=None)
    strikes: list = Field(default=None)
    last_price: float = Field(default=None)
    underlying_name: str = Field(default=None)
    underlying_price: dict = Field(default=None)
    hasIV: bool = Field(default=False)
    hasGreeks: bool = Field(default=False)
    symbol: str = Field(default=None)
    source: str = Field(default=None)
    date: str = Field(default=None)
    SYMBOLS: dict = Field(default=None)
