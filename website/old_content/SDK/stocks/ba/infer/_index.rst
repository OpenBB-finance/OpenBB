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
stocks.ba.infer(
    symbol: str,
    limit: int = 100,
    start_date: Optional[str] = '',
    end_date: Optional[str] = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Load tweets from twitter API and analyzes using VADER
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to search twitter for
    limit: int
        Number of tweets to analyze
    start_date: Optional[str]
        If given, the start time to get tweets from
    end_date: Optional[str]
        If given, the end time to get tweets from
    chart: bool
       Flag to display chart


* **Returns**

    df_tweet: pd.DataFrame
        Dataframe of tweets and sentiment

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.infer(
    symbol: str,
    limit: int = 100,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Infer sentiment from past n tweets
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    limit: int
        Number of tweets to analyze
    export: str
        Format to export tweet dataframe
    chart: bool
       Flag to display chart

