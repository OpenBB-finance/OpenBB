.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get rating over time data. [Source: Finnhub]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dd.rot(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol to get ratings from

    
* **Returns**

    pd.DataFrame
        Get dataframe with ratings
   