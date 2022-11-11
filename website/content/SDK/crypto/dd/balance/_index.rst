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
crypto.dd.balance(
    from_symbol: str,
    to_symbol: str = 'USDT',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get account holdings for asset. [Source: Binance]
    </p>

* **Parameters**

    from_symbol: str
        Cryptocurrency
    to_symbol: str
        Cryptocurrency
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe with account holdings for an asset

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.balance(
    from_symbol: str,
    to_symbol: str = 'USDT',
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get account holdings for asset. [Source: Binance]
    </p>

* **Parameters**

    from_symbol: str
        Cryptocurrency
    to_symbol: str
        Cryptocurrency
    export: str
        Export dataframe data to csv,json,xlsx
    chart: bool
       Flag to display chart

