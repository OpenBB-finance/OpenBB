.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get ETF holdings
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.holdings(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Symbol to get holdings for

    
* **Returns**

    df: *pd.DataFrame*
        Dataframe of holdings
   