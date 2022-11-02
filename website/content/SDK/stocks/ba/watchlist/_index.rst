.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get reddit users watchlists [Source: reddit]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.watchlist(
    limit: int = 5,
    chart: bool = False,
) -> Tuple[List[praw.models.reddit.submission.Submission], dict, int]
{{< /highlight >}}

* **Parameters**

    limit : *int*
        Number of posts to look through

    
* **Returns**

    list[praw.models.reddit.submission.Submission]:
        List of reddit submissions
    dict:
        Dictionary of tickers and counts
    int
        Count of how many posts were analyzed
   