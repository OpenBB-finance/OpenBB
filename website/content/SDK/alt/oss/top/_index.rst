.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get repos sorted by stars or forks. Can be filtered by categories
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
alt.oss.top(
    sortby: str,
    limit: int = 50,
    categories: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby : *str*
            Sort repos by {stars, forks}
    categories : *str*
            Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: *None*
    limit : *int*
            Number of repos to search for
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame with list of repos
