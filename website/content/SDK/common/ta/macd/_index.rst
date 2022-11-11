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
common.ta.macd(
    data: pandas.core.series.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Moving average convergence divergence
    </p>

* **Parameters**

    data: pd.Series
        Values for calculation
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
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
common.ta.macd(
    data: pandas.core.series.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot MACD signal
    </p>

* **Parameters**

    data : pd.Series
        Values to input
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

