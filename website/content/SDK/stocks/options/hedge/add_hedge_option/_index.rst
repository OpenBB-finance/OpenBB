.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Determine the delta, gamma and vega value of the portfolio and/or options.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.options.hedge.add_hedge_option(
    price: float = 100,
    implied_volatility: float = 20,
    strike: float = 120,
    days: float = 30,
    sign: int = 1,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> tuple
{{< /highlight >}}

* **Parameters**

    price: *float*
        The price.
    implied_volatility: *float*
        The implied volatility.
    strike: *float*
        The strike price.
    days: *float*
        The amount of days until expiration. Use annual notation thus a month would be 30 / 360.
    sign: *int*
        Whether you have a long (1) or short (-1) position
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    delta: *float*
    gamma: *float*
    portfolio: *float*
