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
    start\_date: str = '2022-09-30', end\_date: str = '2022-10-30', ) -> List[Dict]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        company ticker to look for news articles
    start\_date: *str*
        date to start searching articles, with format YYYY-MM-DD
    end\_date: *str*
        date to end searching articles, with format YYYY-MM-DD

    
* **Returns**

    articles : *List*
        term to search on the news articles
    