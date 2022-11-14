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
crypto.onchain.top(
    sortby: str = 'rank',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get top 50 tokens. [Source: Ethplorer]

    Returns
    -------
    pd.DataFrame:
        DataFrame with list of top 50 tokens.
    </p>

* **Returns**

    pd.DataFrame:
        DataFrame with list of top 50 tokens.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.top(
    limit: int = 15,
    sortby: str = 'rank',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display top ERC20 tokens [Source: Ethplorer]
    </p>

* **Parameters**

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

