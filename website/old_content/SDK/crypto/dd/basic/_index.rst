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
crypto.dd.basic(
    symbol: str = 'btc-bitcoin',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Basic coin information [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Coin id
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Metric, Value

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.basic(
    symbol: str = 'BTC',
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get basic information for coin. Like:
        name, symbol, rank, type, description, platform, proof_type, contract, tags, parent.
        [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    export: str
        Export dataframe data to csv,json,xlsx
    chart: bool
       Flag to display chart

