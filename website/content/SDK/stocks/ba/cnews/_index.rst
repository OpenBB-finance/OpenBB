.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.cnews(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    chart: bool = False,
) -> List[Dict]
{{< /highlight >}}

.. raw:: html

    <p>
    Get news from a company. [Source: Finnhub]
    </p>

* **Parameters**

    symbol : str
        company ticker to look for news articles
    start_date: str
        date to start searching articles, with format YYYY-MM-DD
    end_date: str
        date to end searching articles, with format YYYY-MM-DD

* **Returns**

    articles : List
        term to search on the news articles
