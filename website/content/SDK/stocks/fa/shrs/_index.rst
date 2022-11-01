.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get shareholders from yahoo
    </h3>

{{< highlight python >}}
stocks.fa.shrs(
    symbol: str,
    holder: str = 'institutional',
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol
    holder : *str*
        Which holder to get table for

    
* **Returns**

    pd.DataFrame
        Major holders
    