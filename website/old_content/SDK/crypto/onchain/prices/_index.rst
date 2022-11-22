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
crypto.onchain.prices(
    address, sortby: str = 'date',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with token historical prices.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.prices(
    address: str,
    limit: int = 30,
    sortby: str = 'date',
    ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display token historical prices with volume and market cap, and average price.
    [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

