.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.hedge.add_hedge_option(
    price: float = 100,
    implied_volatility: float = 20,
    strike: float = 120,
    days: float = 30,
    sign: int = 1,
    chart: bool = False,
) -> tuple
{{< /highlight >}}

.. raw:: html

    <p>
    Determine the delta, gamma and vega value of the portfolio and/or options.
    </p>

* **Parameters**

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
    chart: bool
       Flag to display chart


* **Returns**

    delta: float
    gamma: float
    portfolio: float

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.hedge.add_hedge_option(
    price: float = 100,
    implied_volatility: float = 20,
    strike: float = 120,
    days: float = 30,
    sign: int = 1,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Determine the delta, gamma and vega value of the portfolio and/or options and show them.
    </p>

* **Parameters**

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
    chart: bool
       Flag to display chart


* **Returns**

    delta: float
    gamma: float
    vega: float
