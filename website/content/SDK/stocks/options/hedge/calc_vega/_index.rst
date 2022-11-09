.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.hedge.calc_vega(
    asset_price: float = 100,
    asset_volatility: float = 20,
    strike_price: float = 120,
    time_to_expiration: float = 30,
    risk_free_rate: float = 0,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    The first-order partial-derivative with respect to the underlying asset volatility of
    the Black-Scholes equation is known as vega. Vega refers to how the option value
    changes when there is a change in the underlying asset volatility. Multiplying vega by
    a +-1% change in the underlying asset volatility, holding all other parameters constant, will give
    you the new value of the option. Vega will be positive for long positions and negative for short positions.
    </p>

* **Parameters**

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

* **Returns**

    vega: float
        Returns the value for the gamma.
