.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load tweets from twitter API and analyzes using VADER
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.infer(
    symbol: str,
    limit: int = 100,
    start_date: Optional[str] = '',
    end_date: Optional[str] = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to search twitter for
    limit: *int*
        Number of tweets to analyze
    start_date: Optional[str]
        If given, the start time to get tweets from
    end_date: Optional[str]
        If given, the end time to get tweets from

    
* **Returns**

    df_tweet: *pd.DataFrame*
        Dataframe of tweets and sentiment
    