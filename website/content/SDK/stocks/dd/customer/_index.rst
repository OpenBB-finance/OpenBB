.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dd.customer(
    symbol: str,
    limit: int = 50,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Print customers from ticker provided
    </p>

* **Parameters**

    symbol: str
        Ticker to select customers from
    limit: int
        The maximum number of rows to show

* **Returns**

    pd.DataFrame
        A dataframe of suppliers
