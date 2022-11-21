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
stocks.options.pcr(
    symbol: str,
    window: int = 30,
    start_date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets put call ratio over last time window [Source: AlphaQuery.com]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to look for
    window: int, optional
        Window to consider, by default 30
    start_date: str, optional
        Start date to plot (e.g., 2021-10-01), by default last 366 days
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.pcr(
    symbol: str,
    window: int = 30,
    start_date: str = '2021-11-13',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display put call ratio [Source: AlphaQuery.com]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    window : int, optional
        Window length to look at, by default 30
    start_date : str, optional
        Starting date for data, by default (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

