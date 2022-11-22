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
stocks.ta.recom(
    symbol: str,
    screener: str = 'america',
    exchange: str = '',
    interval: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get tradingview recommendation based on technical indicators
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get the recommendation from tradingview based on technical indicators
    screener : str
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: str
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: str
        Interval time to check technical indicators and correspondent recommendation
    chart: bool
       Flag to display chart


* **Returns**

    df_recommendation: pd.DataFrame
        Dataframe of tradingview recommendations based on technical indicators

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ta.recom(
    symbol: str,
    screener: str = 'america',
    exchange: str = '',
    interval: str = '',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print tradingview recommendation based on technical indicators
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get tradingview recommendation based on technical indicators
    screener : str
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: str
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: str
        Interval time to check technical indicators and correspondent recommendation
    export: str
        Format of export file
    chart: bool
       Flag to display chart

