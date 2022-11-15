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
stocks.dd.pt(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get analysts' price targets for a given stock. [Source: Business Insider]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Analysts data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dd.pt(
    symbol: str,
    data: pandas.core.frame.DataFrame,
    start_date: str = None,
    limit: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display analysts' price targets for a given stock. [Source: Business Insider]
    </p>

* **Parameters**

    symbol: str
        Due diligence ticker symbol
    data: DataFrame
        Due diligence stock dataframe
    start_date : str
        Start date of the stock data, format YYYY-MM-DD
    limit : int
        Number of latest price targets from analysts to print
    raw: bool
        Display raw data only
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

