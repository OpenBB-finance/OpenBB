"""Hedge view"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.hedge import hedge_model

logger = logging.getLogger(__name__)


def add_and_show_greeks(
    price: float = 100,
    implied_volatility: float = 20,
    strike: float = 120,
    days: float = 30,
    sign: int = 1,
):
    """Determine the delta, gamma and vega value of the portfolio and/or options and show them.

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
    vega: float
    """
    # Add in hedge option
    delta, gamma, vega = hedge_model.add_hedge_option(
        price, implied_volatility, strike, days, sign
    )

    # Show the added delta, gamma and vega positions. Next to that, also show the inputted
    # implied volatility and strike
    positions = pd.DataFrame(
        [delta, gamma, vega, implied_volatility, strike],
        index=["Delta", "Gamma", "Vega", "Implied Volatility", "Strike Price"],
        columns=["Positions"],
    )

    # Show table
    print_rich_table(positions, show_index=True, headers=list(positions.columns))

    return delta, gamma, vega


def show_calculated_hedge(
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
    underlying asset to hold a neutral portfolio and show them

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
    A table with the neutral portfolio weights.
    """
    # Calculate hedge position
    (
        weight_option_a,
        weight_option_b,
        weight_shares,
        is_singular,
    ) = hedge_model.calc_hedge(portfolio_option_amount, side, greeks, sign)

    if sum([weight_option_a, weight_option_b, weight_shares]):
        # Show the weights that would create a neutral portfolio
        positions = pd.DataFrame(
            [weight_option_a, weight_option_b, weight_shares],
            index=["Weight Option A", "Weight Option B", "Weight Shares"],
            columns=["Positions"],
        )

        print_rich_table(
            positions,
            title="Neutral Portfolio Weights",
            headers=list(positions.columns),
            show_index=True,
        )

        if is_singular:
            console.print(
                "[red]Warning\n[/red]"
                "The selected combination of options yields multiple solutions.\n"
                "This is the first feasible solution, possibly not the best one."
            )
    else:
        console.print(
            "[red]Due to there being multiple solutions (Singular Matrix) the current options "
            "combination can not be solved. Please input different options.[/red]"
        )
