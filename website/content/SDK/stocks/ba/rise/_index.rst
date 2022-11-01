.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get top rising related queries with this stock's query [Source: google]
    </h3>

{{< highlight python >}}
stocks.ba.rise(
    symbol: str,
    limit: int = 10,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol
    limit: *int*
        Number of queries to show

    
* **Returns**

    pd.DataFrame
        Dataframe containing rising related queries
    