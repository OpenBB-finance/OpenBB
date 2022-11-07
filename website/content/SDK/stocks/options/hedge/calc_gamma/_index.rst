.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.hedge.calc_gamma(
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
    The second-order partial-derivative with respect to the underlying asset of the Black-Scholes equation
    is known as gamma. Gamma refers to how the option’s delta changes when there is a change in the underlying
    asset price. Multiplying gamma by a +-$1 change in the underlying asset, holding all other parameters constant,
    will give you the new value of the option’s delta. Essentially, gamma is telling us the rate of change of delta
    given a +-1 change in the underlying asset price. Gamma is always positive for long positions and
    negative for short positions.
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

    gamma: float
        Returns the value for the gamma.
