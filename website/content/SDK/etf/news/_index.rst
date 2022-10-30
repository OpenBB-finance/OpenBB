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
    start\_date: str = '2022-10-23', show\_newest: bool = True,
    sources: str = '',
    chart: bool = False,
    ) -> List[Tuple[Any, Any]]
{{< /highlight >}}

* **Parameters**

    query : *str*
        term to search on the news articles
    start\_date: *str*
        date to start searching articles from formatted YYYY-MM-DD
    show\_newest: *bool*
        flag to show newest articles first
    sources: *str*
        sources to exclusively show news from

    
* **Returns**

    tables : List[Tuple]
        List of tuples containing news df in first index and dict containing title of news df
    