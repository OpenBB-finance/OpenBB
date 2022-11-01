.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.prices(
    address, sortby: str = 'date',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    address: *str*
        Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8
    sortby: *str*
        Key to sort by.
    ascend: *str*
        Sort in descending order.

    
* **Returns**

    pd.DataFrame:
        DataFrame with token historical prices.
    