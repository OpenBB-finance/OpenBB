.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get tradingview recommendation based on technical indicators
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ta.recom(
    symbol: str,
    screener: str = 'america',
    exchange: str = '',
    interval: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol to get the recommendation from tradingview based on technical indicators
    screener : *str*
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: *str*
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: *str*
        Interval time to check technical indicators and correspondent recommendation

    
* **Returns**

    df_recommendation: *pd.DataFrame*
        Dataframe of tradingview recommendations based on technical indicators
    