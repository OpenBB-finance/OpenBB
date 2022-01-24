"""Option helper functions"""
__docformat__ = "numpy"

from abc import abstractmethod
from math import log, e
from typing import Union
import numpy as np
import pandas as pd
from scipy.stats import norm

from gamestonk_terminal.rich_config import console


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

    loss = []
    for price_at_exp in strikes:
        loss.append(get_loss_at_strike(price_at_exp, chain))

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


class Option:
    def __init__(
        self,
        s: float,
        k: float,
        rf: float,
        div_cont: float,
        expiry: float,
        vol: float,
        opt_type: int = 1,
    ):
        """
        A baseclass for creating options

        Parameters
        ----------
        type : int
            Option type, 1 for call and -1 for a put
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
        """
        self.Type = int(opt_type)
        self.S = float(s)
        self.K = float(k)
        self.r = float(rf)
        self.q = float(div_cont)
        self.T = float(expiry) / 365.0
        self._sigma = float(vol)
        self.sigmaT = self._sigma * self.T ** 0.5

    @property
    @abstractmethod
    def d1(self):
        raise AttributeError("This must be overridden")

    @property
    def d2(self):
        return self.d1 - self.sigmaT


class BSVanilla(Option):
    @property
    def d1(self):
        return (
            log(self.S / self.K) + (self.r - self.q + 0.5 * (self.sigma ** 2)) * self.T
        ) / self.sigmaT

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, val):
        self._sigma = val
        self.sigmaT = val * self.T ** 0.5

    def Premium(self):
        tmpprem = self.Type * (
            self.S * e ** (-self.q * self.T) * norm.cdf(self.Type * self.d1)
            - self.K * e ** (-self.r * self.T) * norm.cdf(self.Type * self.d2)
        )
        return tmpprem

    # 1st order greeks

    def Delta(self):
        dfq = e ** (-self.q * self.T)
        if self.Type == 1:
            return dfq * norm.cdf(self.d1)
        return dfq * (norm.cdf(self.d1) - 1)

    def Vega(self):
        """Vega for 1% change in vol"""
        return (
            0.01 * self.S * e ** (-self.q * self.T) * norm.pdf(self.d1) * self.T ** 0.5
        )

    def Theta(self):
        """Theta for 1 day change"""
        df = e ** -(self.r * self.T)
        dfq = e ** (-self.q * self.T)
        tmptheta = (1.0 / 365.0) * (
            -0.5 * self.S * dfq * norm.pdf(self.d1) * self.sigma / (self.T ** 0.5)
            + self.Type
            * (
                self.q * self.S * dfq * norm.cdf(self.Type * self.d1)
                - self.r * self.K * df * norm.cdf(self.Type * self.d2)
            )
        )
        return tmptheta

    def Rho(self):
        df = e ** -(self.r * self.T)
        return self.Type * self.K * self.T * df * 0.01 * norm.cdf(self.Type * self.d2)

    def Phi(self):
        return (
            0.01
            * -self.Type
            * self.T
            * self.S
            * e ** (-self.q * self.T)
            * norm.cdf(self.Type * self.d1)
        )

    # 2nd order greeks

    def Gamma(self):
        return e ** (-self.q * self.T) * norm.pdf(self.d1) / (self.S * self.sigmaT)

    def Charm(self):
        """Calculates Charm for one day change"""
        dfq = e ** (-self.q * self.T)
        cdf = norm.cdf(self.Type * self.d1)
        return (
            (1.0 / 365.0)
            * -dfq
            * (
                norm.pdf(self.d1)
                * ((self.r - self.q) / (self.sigmaT) - self.d2 / (2 * self.T))
                + (self.Type * -self.q) * cdf
            )
        )

    def Vanna(self):
        """Vanna for 1% change in vol"""
        return (
            0.01 * -(e ** (-self.q * self.T)) * self.d2 / self.sigma * norm.pdf(self.d1)
        )

    def Vomma(self):
        return (
            0.01 * -(e ** (-self.q * self.T)) * self.d2 / self.sigma * norm.pdf(self.d1)
        )
