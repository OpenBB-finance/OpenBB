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
common.ta.kc(
    data: pandas.core.frame.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = 'ema',
    offset: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Keltner Channels
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset : int
        Offset value
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of rolling kc

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.kc(
    data: pandas.core.frame.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = 'ema',
    offset: int = 0,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    View Keltner Channels Indicator
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of ohlc prices
    window: int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset: int
        Offset value
    symbol: str
        Ticker symbol
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

