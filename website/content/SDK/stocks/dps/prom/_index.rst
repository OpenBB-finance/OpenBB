.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get all FINRA ATS data, and parse most promising tickers based on linear regression
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dps.prom(
    limit: int = 1000,
    tier_ats: str = 'T1',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Dict]
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity
    tier_ats : *int*
        Tier to process data from: T1, T2 or OTCE

    
* **Returns**

    pd.DataFrame
        Dark Pools (ATS) Data
    Dict
        Tickers from Dark Pools with better regression slope
    