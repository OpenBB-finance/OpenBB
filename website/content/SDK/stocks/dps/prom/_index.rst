.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dps.prom(
    limit: int = 1000,
    tier_ats: str = 'T1',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Dict]
{{< /highlight >}}

.. raw:: html

    <p>
    Get all FINRA ATS data, and parse most promising tickers based on linear regression
    </p>

* **Parameters**

    limit: int
        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity
    tier_ats : int
        Tier to process data from: T1, T2 or OTCE
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dark Pools (ATS) Data
    Dict
        Tickers from Dark Pools with better regression slope

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dps.prom(
    input_limit: int = 1000,
    limit: int = 10,
    tier: str = 'T1',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]
    </p>

* **Parameters**

    input_limit : int
        Number of tickers to filter from entire ATS data based on
        the sum of the total weekly shares quantity
    limit : int
        Number of tickers to display from most promising with
        better linear regression slope
    tier : str
        Tier to process data from: T1, T2 or OTCE
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

