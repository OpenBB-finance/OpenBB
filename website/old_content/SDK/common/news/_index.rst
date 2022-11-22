.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
common.news(
    term: str = '',
    sources: str = '',
    sort: str = 'published',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get news for a given term and source. [Source: Feedparser]
    </p>

* **Parameters**

    term : str
        term to search on the news articles
    sources: str
        sources to exclusively show news from (separated by commas)
    sort: str
        the column to sort by

* **Returns**

    articles : dict
        term to search on the news articles
