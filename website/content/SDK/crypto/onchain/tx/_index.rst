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
crypto.onchain.tx(
    tx_hash, chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get info about transaction. [Source: Ethplorer]
    </p>

* **Parameters**

    tx_hash: str
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with information about ERC20 token transaction.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.tx(
    tx_hash: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display info about transaction. [Source: Ethplorer]
    </p>

* **Parameters**

    tx_hash: str
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

