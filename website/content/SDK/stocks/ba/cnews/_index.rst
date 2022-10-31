.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get news from a company. [Source: Finnhub]
    </h3>

{{< highlight python >}}
stocks.ba.cnews(
    symbol: str,
    start_date: str = '2022-10-01', end_date: str = '2022-10-31', ) -> List[Dict]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        company ticker to look for news articles
    start_date: *str*
        date to start searching articles, with format YYYY-MM-DD
    end_date: *str*
        date to end searching articles, with format YYYY-MM-DD

    
* **Returns**

    articles : *List*
        term to search on the news articles
    