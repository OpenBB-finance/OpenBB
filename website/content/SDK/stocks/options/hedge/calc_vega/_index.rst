.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > The first-order partial-derivative with respect to the underlying asset volatility of
    the Black-Scholes equation is known as vega. Vega refers to how the option value
    changes when there is a change in the underlying asset volatility. Multiplying vega by
    a +-1% change in the underlying asset volatility, holding all other parameters constant, will give
    you the new value of the option. Vega will be positive for long positions and negative for short positions.
    </h3>

{{< highlight python >}}
stocks.options.hedge.calc_vega(
    asset\_price: float = 100,
    asset\_volatility: float = 20,
    strike\_price: float = 120,
    time\_to\_expiration: float = 30,
    risk\_free\_rate: float = 0,
    )
{{< /highlight >}}

* **Parameters**

    asset\_price: *int*
        The price.
    asset\_volatility: *float*
        The implied volatility.
    strike\_price: *float*
        The strike price.
    time\_to\_expiration: *float*
        The amount of days until expiration. Use annual notation thus a month would be 30 / 360.
    risk\_free\_rate: *float*
        The risk free rate.

    
* **Returns**

    vega: *float*
        Returns the value for the gamma.
    