.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical price correlation. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ca.hcorr(
    similar: List[str],
    start_date: str = '2021-10-31', candle_type: str = 'a',
    chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    