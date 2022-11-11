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
stocks.ba.redditsent(
    symbol: str,
    limit: int = 100,
    sortby: str = 'relevance',
    time_frame: str = 'week',
    full_search: bool = True,
    subreddits: str = 'all',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, list, float]
{{< /highlight >}}

.. raw:: html

    <p>
    Finds posts related to a specific search term in Reddit
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to search for
    limit: int
        Number of posts to get per subreddit
    sortby: str
        Search type
        Possibilities: "relevance", "hot", "top", "new", or "comments"
    time_frame: str
        Relative time of post
        Possibilities: "hour", "day", "week", "month", "year", "all"
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits
    chart: bool
       Flag to display chart


* **Returns**

    tuple[pd.DataFrame, list, float]:
        Dataframe of submissions related to the search term,
        List of polarity scores,
        Average polarity score

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.redditsent(
    symbol: str,
    sortby: str = 'relevance',
    limit: int = 100,
    graphic: bool = False,
    time_frame: str = 'week',
    full_search: bool = True,
    subreddits: str = 'all',
    display: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Determine Reddit sentiment about a search term
    </p>

* **Parameters**

    symbol: str
        The ticker symbol being search for in Reddit
    sortby: str
        Type of search
    limit: str
        Number of posts to get at most
    graphic: bool
        Displays box and whisker plot
    time_frame: str
        Time frame for search
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits
    display: bool
        Enable printing of raw sentiment values for each post
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]]
        If supplied, expect 1 external axis
    chart: bool
       Flag to display chart

