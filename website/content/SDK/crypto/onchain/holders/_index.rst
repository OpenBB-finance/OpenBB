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
crypto.onchain.holders(
    address, sortby: str = 'balance',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get info about top token holders. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with list of top token holders.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.holders(
    address: str,
    limit: int = 10,
    sortby: str = 'balance',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display info about top ERC20 token holders. [Source: Ethplorer]
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

