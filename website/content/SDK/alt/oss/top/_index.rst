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
alt.oss.top(
    sortby: str,
    limit: int = 50,
    categories: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get repos sorted by stars or forks. Can be filtered by categories
    </p>

* **Parameters**

    sortby : str
            Sort repos by {stars, forks}
    categories : str
            Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    limit : int
            Number of repos to search for
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame with list of repos

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
alt.oss.top(
    sortby: str,
    categories: str = '',
    limit: int = 10,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display repo summary [Source: https://api.github.com]
    </p>

* **Parameters**

    sortby : str
        Sort repos by {stars, forks}
    categories : str
        Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    limit : int
        Number of repos to look at
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

