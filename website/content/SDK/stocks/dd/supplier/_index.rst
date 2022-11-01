.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get suppliers from ticker provided. [Source: CSIMarket]
    </h3>

{{< highlight python >}}
stocks.dd.supplier(
    symbol: str,
    limit: int = 50
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to select suppliers from
    limit: *int*
        The maximum number of rows to show

    
* **Returns**

    pd.DataFrame
        A dataframe of suppliers
    