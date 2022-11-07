.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.hedge.calc_delta(
    asset_price: float = 100,
    asset_volatility: float = 20,
    strike_price: float = 120,
    time_to_expiration: float = 30,
    risk_free_rate: float = 0,
    sign: int = 1,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    The first-order partial-derivative with respect to the underlying asset of the Black-Scholes
    equation is known as delta. Delta refers to how the option value changes when there is a change in
    the underlying asset price. Multiplying delta by a +-$1 change in the underlying asset, holding all other
    parameters constant, will give you the new value of the option. Delta will be positive for long call and
    short put positions, negative for short call and long put positions.
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
    sign: int
        Whether you have a long (1) or short (-1) position

* **Returns**

    delta: float
        Returns the value for the delta.
