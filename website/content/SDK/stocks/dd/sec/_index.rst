.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get SEC filings for a given stock ticker. [Source: Market Watch]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dd.sec(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    df_financials : *pd.DataFrame*
        SEC filings data
   