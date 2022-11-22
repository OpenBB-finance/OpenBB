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
common.ta.fisher(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Fisher Transform
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of OHLC prices
    window: int
        Length for indicator window
    chart: bool
       Flag to display chart


* **Returns**

    df_ta: pd.DataFrame
        Dataframe of technical indicator

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.fisher(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Fisher Indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of OHLC prices
    window : int
        Length of window
    symbol : str
        Ticker string
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

