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
crypto.dd.trades(
    symbol: str,
    limit: int = 1000,
    side: Optional[Any] = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get last N trades for chosen trading pair. [Source: Coinbase]
    </p>

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: *int*
        Last <limit> of trades. Maximum is 1000.
    side: *str*
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Last N trades for chosen trading pairs.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.trades(
    symbol: str,
    limit: int = 20,
    side: Optional[str] = None,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display last N trades for chosen trading pair. [Source: Coinbase]
    </p>

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: *int*
        Last <limit> of trades. Maximum is 1000.
    side: Optional[str]
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    export : *str*
        Export dataframe data to csv,json,xlsx file
    chart: *bool*
       Flag to display chart

