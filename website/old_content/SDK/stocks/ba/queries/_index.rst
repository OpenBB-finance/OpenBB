.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.queries(
    symbol: str,
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get related queries from google api [Source: google]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol to compare
    limit: int
        Number of queries to show

* **Returns**

    dict : {'top': pd.DataFrame or None, 'rising': pd.DataFrame or None}
