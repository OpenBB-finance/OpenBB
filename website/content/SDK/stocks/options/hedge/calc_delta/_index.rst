.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > The first-order partial-derivative with respect to the underlying asset of the Black-Scholes
    equation is known as delta. Delta refers to how the option value changes when there is a change in
    the underlying asset price. Multiplying delta by a +-$1 change in the underlying asset, holding all other
    parameters constant, will give you the new value of the option. Delta will be positive for long call and
    short put positions, negative for short call and long put positions.
    </h3>

{{< highlight python >}}
stocks.options.hedge.calc_delta(
    asset\_price: float = 100,
    asset\_volatility: float = 20,
    strike\_price: float = 120,
    time\_to\_expiration: float = 30,
    risk\_free\_rate: float = 0,
    sign: int = 1,
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
    sign: *int*
        Whether you have a long (1) or short (-1) position

    
* **Returns**

    delta: *float*
        Returns the value for the delta.
    