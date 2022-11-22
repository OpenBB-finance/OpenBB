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
common.ta.vwap(
    data: pandas.core.series.Series,
    offset: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets volume weighted average price (VWAP)
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of dates and prices
    offset: int
        Length of offset
    chart: bool
       Flag to display chart


* **Returns**

    df_vwap: pd.DataFrame
        Dataframe with VWAP data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.vwap(
    data: pandas.core.frame.DataFrame,
    symbol: str = '',
    start_date: str = None,
    end_date: str = None,
    offset: int = 0,
    interval: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plots VWMA technical indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of OHLC prices
    symbol : str
        Ticker
    offset : int
        Offset variable
    start_date: datetime
        Start date to get data from with
    end_date: datetime
        End date to get data from with
    interval : str
        Interval of data
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

