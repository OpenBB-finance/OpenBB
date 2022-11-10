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
stocks.ba.watchlist(
    limit: int = 5,
    chart: bool = False,
) -> Tuple[List[praw.models.reddit.submission.Submission], dict, int]
{{< /highlight >}}

.. raw:: html

    <p>
    Get reddit users watchlists [Source: reddit]
    </p>

* **Parameters**

    limit : int
        Number of posts to look through
    chart: bool
       Flag to display chart


* **Returns**

    list[praw.models.reddit.submission.Submission]:
        List of reddit submissions
    dict:
        Dictionary of tickers and counts
    int
        Count of how many posts were analyzed

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.watchlist(
    limit: int = 5,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print other users watchlist. [Source: Reddit]
    </p>

* **Parameters**

    limit: int
        Maximum number of submissions to look at
    chart: bool
       Flag to display chart

