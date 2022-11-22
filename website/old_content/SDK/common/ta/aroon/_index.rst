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
common.ta.aroon(
    data: pandas.core.frame.DataFrame,
    window: int = 25,
    scalar: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Aroon technical indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe with OHLC price data
    window : int
        Length of window
    scalar : int
        Scalar variable
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame with aroon indicator

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.aroon(
    data: pandas.core.frame.DataFrame,
    window: int = 25,
    scalar: int = 100,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot Aroon indicator
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe with OHLC price data
    window: int
        Length of window
    symbol: str
        Ticker
    scalar: int
        Scalar variable
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

