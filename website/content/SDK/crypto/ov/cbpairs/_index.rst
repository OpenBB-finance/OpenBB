.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get a list of available currency pairs for trading. [Source: Coinbase]

    base_min_size - min order size
    base_max_size - max order size
    min_market_funds -  min funds allowed in a market order.
    max_market_funds - max funds allowed in a market order.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cbpairs(
    limit: int = 50,
    sortby: str = 'quote_increment',
    ascend: bool = True,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Top n of pairs
    sortby: *str*
        Key to sortby data
    ascend: *bool*
        Sort descending flag

    
* **Returns**

    pd.DataFrame
        Available trading pairs on Coinbase
    