"""Hedge model"""
__docformat__ = "numpy"

import math

import numpy as np
from scipy.stats import norm

# Based on article of Roman Paolucci: https://towardsdatascience.com/algorithmic-portfolio-hedging-9e069aafff5a


def calc_hedge(
    portfolio_option_amount: float = 100,
    side: str = "Call",
    greeks: dict = {
        "Portfolio": {
            "Delta": 1,
            "Gamma": 9.1268e-05,
            "Vega": 5.4661,
        },
        "Option A": {
            "Delta": 1,
            "Gamma": 9.1268e-05,
            "Vega": 5.4661,
        },
        "Option B": {
            "Delta": 1,
            "Gamma": 9.1268e-05,
            "Vega": 5.4661,
        },
    },
    sign: int = 1,
):
    """Determine the hedge position and the weights within each option and
    underlying asset to hold a neutral portfolio

    Parameters
    ----------
    portfolio_option_amount: float
        Number to show
    side: str
        Whether you have a Call or Put instrument
    greeks: dict
        Dictionary containing delta, gamma and vega values for the portfolio and option A and B. Structure is
        as follows: {'Portfolio': {'Delta': VALUE, 'Gamma': VALUE, 'Vega': VALUE}} etc
    sign: int
        Whether you have a long (1) or short (-1) position

    Returns
    -------
    option A weight: float
    option B weight: float
    portfolio weight: float
    is_singular: boolean
    """
    # Shortnames for delta, gamma and vega of portfolio
    portfolio_option_delta = greeks["Portfolio"]["Delta"]
    portfolio_option_gamma = greeks["Portfolio"]["Gamma"]
    portfolio_option_vega = greeks["Portfolio"]["Vega"]

    # Shortnames for delta, gamma and vega of option A
    option_a_delta = greeks["Option A"]["Delta"]
    option_a_gamma = greeks["Option A"]["Gamma"]
    option_a_vega = greeks["Option A"]["Vega"]

    # Shortnames for delta, gamma and vega of option B
    option_b_delta = greeks["Option B"]["Delta"]
    option_b_gamma = greeks["Option B"]["Gamma"]
    option_b_vega = greeks["Option B"]["Vega"]

    # Delta will be positive for long call and short put positions, negative for short call and long put positions.
    delta_multiplier = 1

    # Gamma is always positive for long positions and negative for short positions.
    gamma_multiplier = 1

    # Vega will be positive for long positions and negative for short positions.
    vega_multiplier = 1

    # Initialize variable
    short = False

    # Short position
    if sign == -1:
        short = True
        gamma_multiplier = -1
        vega_multiplier = -1
        if side == "Call":
            # Short call position
            delta_multiplier = -1
    elif side == "Put" and sign == 1:
        # Long put position
        delta_multiplier = -1

    options_array = np.array(
        [[option_a_gamma, option_b_gamma], [option_a_vega, option_b_vega]]
    )

    portfolio_greeks = [
        [portfolio_option_gamma * portfolio_option_amount],
        [portfolio_option_vega * portfolio_option_amount],
    ]

    singular = False
    try:
        inv = np.linalg.inv(np.round(options_array, 2))
    except np.linalg.LinAlgError:
        options_array = np.round(options_array, 2)
        a = options_array.shape[0]
        i = np.eye(a, a)
        inv = np.linalg.lstsq(options_array, i)[0]
        singular = True

    weights = np.dot(inv, portfolio_greeks)

    portfolio_greeks = [
        [portfolio_option_delta * delta_multiplier * portfolio_option_amount],
        [portfolio_option_gamma * gamma_multiplier * portfolio_option_amount],
        [portfolio_option_vega * vega_multiplier * portfolio_option_amount],
    ]

    options_array = np.array(
        [
            [option_a_delta, option_b_delta],
            [option_a_gamma, option_b_gamma],
            [option_a_vega, option_b_vega],
        ]
    )

    if not short:
        neutral = np.round(
            np.dot(np.round(options_array, 2), weights) - portfolio_greeks
        )
    else:
        neutral = np.round(
            np.dot(np.round(options_array, 2), weights) + portfolio_greeks
        )

    return weights[0][0], weights[1][0], neutral[0][0], singular


def add_hedge_option(
    price: float = 100,
    implied_volatility: float = 20,
    strike: float = 120,
    days: float = 30,
    sign: int = 1,
) -> tuple:
    """Determine the delta, gamma and vega value of the portfolio and/or options.

    Parameters
    ----------
    price: float
        The price.
    implied_volatility: float
        The implied volatility.
    strike: float
        The strike price.
    days: float
        The amount of days until expiration. Use annual notation thus a month would be 30 / 360.
    sign: int
        Whether you have a long (1) or short (-1) position

    Returns
    -------
    delta: float
    gamma: float
    portfolio: float
    """
    # Determine delta position given the option
    delta = calc_delta(price, implied_volatility, strike, days, 0, sign)

    # Determine gamma position given the option
    gamma = calc_gamma(price, implied_volatility, strike, days, 0)

    # Determine vega position given the option
    vega = calc_vega(price, implied_volatility, strike, days, 0)

    return delta, gamma, vega


def calc_delta(
    asset_price: float = 100,
    asset_volatility: float = 20,
    strike_price: float = 120,
    time_to_expiration: float = 30,
    risk_free_rate: float = 0,
    sign: int = 1,
):
    """The first-order partial-derivative with respect to the underlying asset of the Black-Scholes
    equation is known as delta. Delta refers to how the option value changes when there is a change in
    the underlying asset price. Multiplying delta by a +-$1 change in the underlying asset, holding all other
    parameters constant, will give you the new value of the option. Delta will be positive for long call and
    short put positions, negative for short call and long put positions.

    Parameters
    ----------
    asset_price: int
        The price.
    asset_volatility: float
        The implied volatility.
    strike_price: float
        The strike price.
    time_to_expiration: float
        The amount of days until expiration. Use annual notation thus a month would be 30 / 360.
    risk_free_rate: float
        The risk free rate.
    sign: int
        Whether you have a long (1) or short (-1) position

    Returns
    -------
    delta: float
        Returns the value for the delta.
    """
    b = math.exp(-risk_free_rate * time_to_expiration)
    x1 = (
        math.log(asset_price / (b * strike_price))
        + 0.5 * (asset_volatility * asset_volatility) * time_to_expiration
    )
    x1 = x1 / (asset_volatility * (time_to_expiration**0.5))
    delta = norm.cdf(x1)

    if sign == 1:
        return delta

    return delta - 1


def calc_gamma(
    asset_price: float = 100,
    asset_volatility: float = 20,
    strike_price: float = 120,
    time_to_expiration: float = 30,
    risk_free_rate: float = 0,
):
    """The second-order partial-derivative with respect to the underlying asset of the Black-Scholes equation
    is known as gamma. Gamma refers to how the option’s delta changes when there is a change in the underlying
    asset price. Multiplying gamma by a +-$1 change in the underlying asset, holding all other parameters constant,
    will give you the new value of the option’s delta. Essentially, gamma is telling us the rate of change of delta
    given a +-1 change in the underlying asset price. Gamma is always positive for long positions and
    negative for short positions.

    Parameters
    ----------
    asset_price: int
        The price.
    asset_volatility: float
        The implied volatility.
    strike_price: float
        The strike price.
    time_to_expiration: float
        The amount of days until expiration. Use annual notation thus a month would be 30 / 360.
    risk_free_rate: float
        The risk free rate.

    Returns
    -------
    gamma: float
        Returns the value for the gamma.
    """
    b = math.exp(-risk_free_rate * time_to_expiration)
    x1 = (
        math.log(asset_price / (b * strike_price))
        + 0.5 * (asset_volatility * asset_volatility) * time_to_expiration
    )
    x1 = x1 / (asset_volatility * (time_to_expiration**0.5))
    z1 = norm.cdf(x1)
    gamma = z1 / (asset_price * asset_volatility * math.sqrt(time_to_expiration))

    return gamma


def calc_vega(
    asset_price: float = 100,
    asset_volatility: float = 20,
    strike_price: float = 120,
    time_to_expiration: float = 30,
    risk_free_rate: float = 0,
):
    """The first-order partial-derivative with respect to the underlying asset volatility of
    the Black-Scholes equation is known as vega. Vega refers to how the option value
    changes when there is a change in the underlying asset volatility. Multiplying vega by
    a +-1% change in the underlying asset volatility, holding all other parameters constant, will give
    you the new value of the option. Vega will be positive for long positions and negative for short positions.

    Parameters
    ----------
    asset_price: int
        The price.
    asset_volatility: float
        The implied volatility.
    strike_price: float
        The strike price.
    time_to_expiration: float
        The amount of days until expiration. Use annual notation thus a month would be 30 / 360.
    risk_free_rate: float
        The risk free rate.

    Returns
    -------
    vega: float
        Returns the value for the gamma.
    """
    b = math.exp(-risk_free_rate * time_to_expiration)
    x1 = (
        math.log(asset_price / (b * strike_price))
        + 0.5 * (asset_volatility * asset_volatility) * time_to_expiration
    )
    x1 = x1 / (asset_volatility * (time_to_expiration**0.5))
    z1 = norm.cdf(x1)
    vega = asset_price * z1 * math.sqrt(time_to_expiration)

    return vega / 100
