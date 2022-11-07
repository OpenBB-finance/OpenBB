.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.rise(
    symbol: str,
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get top rising related queries with this stock's query [Source: google]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    limit: int
        Number of queries to show

* **Returns**

    pd.DataFrame
        Dataframe containing rising related queries
