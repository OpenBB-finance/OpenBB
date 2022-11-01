.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get fundamental data from finviz
    </h3>

{{< highlight python >}}
stocks.fa.data(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        DataFrame of fundamental data
    