.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get sentiments from symbol
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.sentiment(
    symbol: str,
    n_tweets: int = 15,
    n_days_past: int = 2,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol to get sentiment for
    n_tweets: *int*
        Number of tweets to get per hour
    n_days_past: *int*
        Number of days to extract tweets for
    