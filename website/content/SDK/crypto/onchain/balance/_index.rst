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
crypto.onchain.balance(
    address: str,
    sortby: str = 'index',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which
    have name and symbol. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with list of tokens and their balances.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.balance(
    address: str,
    limit: int = 15,
    sortby: str = 'index',
    ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display info about tokens for given ethereum blockchain balance e.g. ETH balance,
    balance of all tokens with name and symbol. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Ethereum balance.
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

