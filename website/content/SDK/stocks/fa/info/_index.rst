.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets ticker symbol info
    </h3>

{{< highlight python >}}
stocks.fa.info(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        DataFrame of yfinance information
    