.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get a list of available currency pairs for trading. [Source: Coinbase]

    base\_min\_size - min order size
    base\_max\_size - max order size
    min\_market\_funds -  min funds allowed in a market order.
    max\_market\_funds - max funds allowed in a market order.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cbpairs(
    limit: int = 50,
    sortby: str = 'quote\_increment', ascend: bool = True,
    chart: bool = False,
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
    