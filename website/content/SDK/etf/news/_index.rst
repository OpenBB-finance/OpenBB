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
etf.news(
    query: str,
    limit: int = 10,
    start_date: str = None,
    show_newest: bool = True,
    sources: str = '',
    chart: bool = False,
) -> List[Tuple[Any, Any]]
{{< /highlight >}}

.. raw:: html

    <p>
    Get news for a given term. [Source: NewsAPI]
    </p>

* **Parameters**

    query : str
        term to search on the news articles
    start_date: str
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from (comma separated)
    chart: bool
       Flag to display chart


* **Returns**

    tables : List[Tuple]
        List of tuples containing news df in first index and dict containing title of news df

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.news(
    query: str,
    limit: int = 3,
    start_date: str = None,
    show_newest: bool = True,
    sources: str = '',
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display news for a given term. [Source: NewsAPI]
    </p>

* **Parameters**

    query : str
        term to search on the news articles
    start_date: str
        date to start searching articles from formatted YYYY-MM-DD
    limit : int
        number of articles to display
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

