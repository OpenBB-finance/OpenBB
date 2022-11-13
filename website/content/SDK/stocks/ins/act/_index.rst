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
stocks.ins.act(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get insider activity. [Source: Business Insider]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get insider activity data from
    chart: bool
       Flag to display chart


* **Returns**

    df_insider : pd.DataFrame
        Get insider activity data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ins.act(
    data: pandas.core.frame.DataFrame,
    symbol: str,
    start_date: str = None,
    interval: str = '1440min',
    limit: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display insider activity. [Source: Business Insider]
    </p>

* **Parameters**

    data: pd.DataFrame
        Stock dataframe
    symbol: str
        Due diligence ticker symbol
    start_date: str
        Initial date (e.g., 2021-10-01). Defaults to 3 years back
    interval: str
        Stock data interval
    limit: int
        Number of latest days of inside activity
    raw: bool
        Print to console
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

