.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dd.supplier(
    symbol: str,
    limit: int = 50,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get suppliers from ticker provided. [Source: CSIMarket]
    </p>

* **Parameters**

    symbol: str
        Ticker to select suppliers from
    limit: int
        The maximum number of rows to show

* **Returns**

    pd.DataFrame
        A dataframe of suppliers
