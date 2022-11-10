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
forex.oanda.candles(
    instrument: Optional[str] = None,
    granularity: str = 'D',
    candlecount: int = 180,
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request data for candle chart.
    </p>

* **Parameters**

    instrument : str
        Loaded currency pair code
    granularity : str, optional
        Data granularity, by default "D"
    candlecount : int, optional
        Limit for the number of data points, by default 180
    chart: bool
       Flag to display chart


* **Returns**

    Union[pd.DataFrame, bool]
        Candle chart data or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.candles(
    instrument: str = '',
    granularity: str = 'D',
    candlecount: int = 180,
    additional_charts: Optional[Dict[str, bool]] = None,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show candle chart.

    Note that additional plots (ta indicators) not supported in external axis mode.
    </p>

* **Parameters**

    instrument : str
        The loaded currency pair
    granularity : str, optional
        The timeframe to get for the candle chart. Seconds: S5, S10, S15, S30
        Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12
        Day (default): D, Week: W Month: M,
    candlecount : int, optional
        Limit for the number of data points
    additional_charts : Dict[str, bool]
        A dictionary of flags to include additional charts
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

