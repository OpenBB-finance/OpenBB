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
stocks.fa.mktcap(
    symbol: str,
    start_date: str = None,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Get market cap over time for ticker. [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbol: str
        Ticker to get market cap over time
    start_date: str
        Initial date (e.g., 2021-10-01). Defaults to 3 years back
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        Dataframe of estimated market cap over time
    str:
        Currency of ticker

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.fa.mktcap(
    symbol: str,
    start_date: str = None,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display market cap over time. [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    start_date: str
        Initial date (e.g., 2021-10-01). Defaults to 3 years back
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

