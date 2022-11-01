.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets Sentiment analysis from several symbols provided by FinBrain's API
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ca.sentiment(
    symbols: List[str],
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbols : List[str]
        List of tickers to get sentiment
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().

    
* **Returns**

    pd.DataFrame
        Contains sentiment analysis from several tickers
    