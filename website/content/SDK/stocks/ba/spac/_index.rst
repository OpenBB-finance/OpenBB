.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.spac(
    limit: int = 5,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, dict, int]
{{< /highlight >}}

.. raw:: html

    <p>
    Get posts containing SPAC from top subreddits [Source: reddit]
    </p>

* **Parameters**

    limit : int, optional
        Number of posts to get for each subreddit, by default 5

* **Returns**

    pd.DataFrame :
        Dataframe of reddit submissions
    dict :
        Dictionary of tickers and counts
    int :
        Number of posts found.
