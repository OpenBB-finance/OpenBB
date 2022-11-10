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
crypto.onchain.hist(
    address, sortby: str = 'timestamp',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get information about balance historical transactions. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with balance historical transactions (last 100)

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.hist(
    address: str,
    limit: int = 10,
    sortby: str = 'timestamp',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display information about balance historical transactions. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Ethereum blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

