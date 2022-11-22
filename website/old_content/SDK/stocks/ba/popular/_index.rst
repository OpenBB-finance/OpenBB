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
stocks.ba.popular(
    limit: int = 10,
    post_limit: int = 50,
    subreddits: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get popular tickers from list of subreddits [Source: reddit]
    </p>

* **Parameters**

    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of top tickers from supplied subreddits

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.popular(
    limit: int = 10,
    post_limit: int = 50,
    subreddits: str = '',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print latest popular tickers. [Source: Reddit]
    </p>

* **Parameters**

    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    export : str
        Format to export dataframe
    chart: bool
       Flag to display chart

