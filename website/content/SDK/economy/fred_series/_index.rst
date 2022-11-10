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
economy.fred_series(
    series_ids: List[str],
    start_date: str = None,
    end_date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get Series data. [Source: FRED]
    </p>

* **Parameters**

    series_ids : List[str]
        Series ID to get data from
    start_date : str
        Start date to get data from, format yyyy-mm-dd
    end_date : str
        End data to get from, format yyyy-mm-dd
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Series data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.fred_series(
    series_ids: List[str],
    start_date: str = None,
    end_date: str = None,
    limit: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]
    </p>

* **Parameters**

    series_ids : List[str]
        FRED Series ID from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3
    start_date : str
        Starting date (YYYY-MM-DD) of data
    end_date : str
        Ending date (YYYY-MM-DD) of data
    limit : int
        Number of data points to display.
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

