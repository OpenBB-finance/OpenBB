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
common.ta.cci(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    scalar: float = 0.0015,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Commodity channel index
    </p>

* **Parameters**

    high_vals: pd.Series
        High values
    low_values: pd.Series
        Low values
    close-values: pd.Series
        Close values
    window: int
        Length of window
    scalar: float
        Scalar variable
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
common.ta.cci(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    scalar: float = 0.0015,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display CCI Indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of OHLC
    window : int
        Length of window
    scalar : float
        Scalar variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

