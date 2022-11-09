.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.price(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Returns price and confidence interval from pyth live feed. [Source: Pyth]
    </p>

* **Parameters**

    symbol : str
        Symbol of the asset to get price and confidence interval from

* **Returns**

    float
        Price of the asset
    float
        Confidence level
    float
        Previous price of the asset
