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
crypto.onchain.info(
    address, chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get info about ERC20 token. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with information about provided ERC20 token.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.info(
    address: str,
    social: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display info about ERC20 token. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    social: bool
        Flag to display social media links
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

