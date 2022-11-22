.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.shrs(
    symbol: str,
    holder: str = 'institutional',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get shareholders from yahoo
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    holder : str
        Which holder to get table for

* **Returns**

    pd.DataFrame
        Major holders
