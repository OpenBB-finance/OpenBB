.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get popular tickers from list of subreddits [Source: reddit]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.ba.popular(
    limit: int = 10,
    post_limit: int = 50,
    subreddits: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit : *int*
        Number of top tickers to get
    post_limit : *int*
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        DataFrame of top tickers from supplied subreddits
