.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Search CoinPaprika. [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.disc.cpsearch(
    query: str,
    category: Optional[Any] = None,
    modifier: Optional[Any] = None,
    sortby: str = 'id',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    query: * str*
        phrase for search
    category:  Optional[Any]
        one or more categories (comma separated) to search.
        Available options: currencies|exchanges|icos|people|tags
        Default: currencies,exchanges,icos,people,tags
    modifier: Optional[Any]
        set modifier for search results. Available options: symbol_search -
        search only by symbol (works for currencies only)
    sortby: *str*
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get)
    ascend: *bool*
        Flag to sort data descending
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pandas.DataFrame
        Search Results
        Columns: Metric, Value
