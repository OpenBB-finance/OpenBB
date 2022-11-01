.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get all FINRA data associated with a ticker
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dps.dpotc(
    symbol: str,
    chart: bool = False
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker to get data from

    
* **Returns**

    pd.DataFrame
        Dark Pools (ATS) Data
    pd.DataFrame
        OTC (Non-ATS) Data
    