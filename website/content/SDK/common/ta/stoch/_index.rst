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
common.ta.stoch(
    data: pandas.core.frame.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Stochastic oscillator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of OHLC prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
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
common.ta.stoch(
    data: pandas.core.frame.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Plot stochastic oscillator signal
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of OHLC prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    symbol : str
        Stock ticker symbol
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

