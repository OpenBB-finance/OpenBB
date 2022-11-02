.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get news for a given term. [Source: NewsAPI]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.news(
    query: str,
    limit: int = 10,
    start_date: str = '2022-10-26',
    show_newest: bool = True,
    sources: str = '',
    chart: bool = False,
) -> List[Tuple[Any, Any]]
{{< /highlight >}}

* **Parameters**

    query : *str*
        term to search on the news articles
    start_date: *str*
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: *bool*
        flag to show newest articles first
    sources: *str*
        sources to exclusively show news from (comma separated)

    
* **Returns**

    tables : List[Tuple]
        List of tuples containing news df in first index and dict containing title of news df
    