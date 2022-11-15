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
stocks.dps.ftd(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    limit: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Display fails-to-deliver data for a given ticker. [Source: SEC]
    </p>

* **Parameters**

    symbol : str
        Stock ticker
    start_date : str
        Start of data, in YYYY-MM-DD format
    end_date : str
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Fail to deliver data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dps.ftd(
    symbol: str,
    data: pandas.core.frame.DataFrame = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 0,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display fails-to-deliver data for a given ticker. [Source: SEC]
    </p>

* **Parameters**

    symbol: str
        Stock ticker
    data: pd.DataFrame
        Stock data
    start_date: str
        Start of data, in YYYY-MM-DD format
    end_date: str
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed
    raw: bool
        Print raw data
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

