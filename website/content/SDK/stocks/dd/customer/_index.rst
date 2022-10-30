.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Print customers from ticker provided
    </h3>

{{< highlight python >}}
stocks.dd.customer(
    symbol: str,
    limit: int = 50,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to select customers from
    limit: *int*
        The maximum number of rows to show

    
* **Returns**

    pd.DataFrame
        A dataframe of suppliers
    