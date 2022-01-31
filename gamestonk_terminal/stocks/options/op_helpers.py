"""Option helper functions"""
__docformat__ = "numpy"

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
        Class for getting the greeks of options. Inspiration from:
        http://www.smileofthales.com/computation/option-pricing-python-inheritance/

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
        dfq = e ** (-self.div_cont * self.exp_time)
        if self.Type == 1:
            return dfq * norm.cdf(self.d1)
        return dfq * (norm.cdf(self.d1) - 1)

    def Vega(self):
        """Vega for 1% change in vol"""
        return (
            0.01
            * self.price
            * e ** (-self.div_cont * self.exp_time)
            * norm.pdf(self.d1)
            * self.exp_time**0.5
        )

    def Theta(self):
        """Theta for 1 day change"""
        df = e ** -(self.risk_free * self.exp_time)
        dfq = e ** (-self.div_cont * self.exp_time)
        tmptheta = (1.0 / 365.0) * (
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
        df = e ** -(self.risk_free * self.exp_time)
        return (
            self.Type
            * self.strike
            * self.exp_time
            * df
            * 0.01
            * norm.cdf(self.Type * self.d2)
        )

    def Phi(self):
        return (
            0.01
            * -self.Type
            * self.exp_time
            * self.price
            * e ** (-self.div_cont * self.exp_time)
            * norm.cdf(self.Type * self.d1)
        )

    # 2nd order greeks

    def Gamma(self):
        return (
            e ** (-self.div_cont * self.exp_time)
            * norm.pdf(self.d1)
            / (self.price * self.sigmaT)
        )

    def Charm(self):
        """Calculates Charm for one day change"""
        dfq = e ** (-self.div_cont * self.exp_time)
        cdf = norm.cdf(self.Type * self.d1)
        return (
            (1.0 / 365.0)
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
        -------
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
        -------
        num : float
            The Vomma

        """
        return (
            change
            * -(e ** (-self.div_cont * self.exp_time))
            * self.d2
            / self.sigma
            * norm.pdf(self.d1)
        )
