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
common.ta.ma(
    data: pandas.core.series.Series,
    window: List[int] = None,
    offset: int = 0,
    ma_type: str = 'EMA',
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Plots MA technical indicator
    </p>

* **Parameters**

    data: pd.Series
        Series of prices
    window: List[int]
        Length of EMA window
    offset: int
        Offset variable
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    symbol: str
        Ticker
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.ma(
    data: pandas.core.series.Series,
    window: List[int] = None,
    offset: int = 0,
    ma_type: str = 'EMA',
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Plots MA technical indicator
    </p>

* **Parameters**

    data: pd.Series
        Series of prices
    window: List[int]
        Length of EMA window
    offset: int
        Offset variable
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    symbol: str
        Ticker
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

