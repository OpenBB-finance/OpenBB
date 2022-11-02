.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Screener Overview
    </h3>

{{< highlight python >}}
stocks.ca.screener(
    similar: List[str],
    data_type: str = 'overview',
)
{{< /highlight >}}

* **Parameters**

    similar:
        List of similar companies.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    data_type : *str*
        Data type between: overview, valuation, financial, ownership, performance, technical

* **Returns**

    pd.DataFrame
        Dataframe with overview, valuation, financial, ownership, performance or technical
