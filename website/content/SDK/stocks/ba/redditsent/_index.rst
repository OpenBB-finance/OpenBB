.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Finds posts related to a specific search term in Reddit
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.redditsent(
    symbol: str,
    limit: int = 100,
    sortby: str = 'relevance',
    time_frame: str = 'week',
    full_search: bool = True,
    subreddits: str = 'all',
    chart: bool = False
) -> Tuple[pandas.core.frame.DataFrame, list, float]
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to search for
    limit: *int*
        Number of posts to get per subreddit
    sortby: *str*
        Search type
        Possibilities: "relevance", "hot", "top", "new", or "comments"
    time_frame: *str*
        Relative time of post
        Possibilities: "hour", "day", "week", "month", "year", "all"
    full_search: *bool*
        Enable comprehensive search for ticker
    subreddits: *str*
        Comma-separated list of subreddits

    
* **Returns**

    tuple[pd.DataFrame, list, float]:
        Dataframe of submissions related to the search term,
        List of polarity scores,
        Average polarity score
    