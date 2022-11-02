.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get news for a given term and source. [Source: Feedparser]
    </h3>

{{< highlight python >}}
common.news(
    term: str = '',
    sources: str = '',
    sort: str = 'published',
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    term : *str*
        term to search on the news articles
    sources: *str*
        sources to exclusively show news from (separated by commas)
    sort: *str*
        the column to sort by

    
* **Returns**

    articles : *dict*
        term to search on the news articles
   