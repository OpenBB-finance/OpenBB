To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.hedge.add_hedge_option(price: float = 100, implied_volatility: float = 20, strike: float = 120, days: float = 30, sign: int = 1) -> tuple

Determine the delta, gamma and vega value of the portfolio and/or options.

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

## Getting charts 
### stocks.options.hedge.add_hedge_option(price: float = 100, implied_volatility: float = 20, strike: float = 120, days: float = 30, sign: int = 1, chart=True)

Determine the delta, gamma and vega value of the portfolio and/or options and show them.

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
