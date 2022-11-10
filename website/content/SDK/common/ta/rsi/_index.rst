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
common.ta.rsi(
    data: pandas.core.series.Series,
    window: int = 14,
    scalar: float = 100,
    drift: int = 1,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Relative strength index
    </p>

* **Parameters**

    data: pd.Series
        Dataframe of prices
    window: int
        Length of window
    scalar: float
        Scalar variable
    drift: int
        Drift variable
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of technical indicator

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.rsi(
    data: pandas.core.series.Series,
    window: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display RSI Indicator
    </p>

* **Parameters**

    data : pd.Series
        Values to input
    window : int
        Length of window
    scalar : float
        Scalar variable
    drift : int
        Drift variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

