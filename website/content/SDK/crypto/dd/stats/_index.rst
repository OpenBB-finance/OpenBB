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
crypto.dd.stats(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]
    </p>

* **Parameters**

    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        24h stats for chosen trading pair

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.stats(
    symbol: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]
    </p>

* **Parameters**

    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

