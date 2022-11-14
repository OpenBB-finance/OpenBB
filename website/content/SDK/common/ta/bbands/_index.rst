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
common.ta.bbands(
    data: pandas.core.frame.DataFrame,
    window: int = 15,
    n_std: float = 2,
    mamode: str = 'ema',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate Bollinger Bands
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    chart: bool
       Flag to display chart


* **Returns**

    df_ta: pd.DataFrame
        Dataframe of bollinger band data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.bbands(
    data: pandas.core.frame.DataFrame,
    symbol: str = '',
    window: int = 15,
    n_std: float = 2,
    mamode: str = 'sma',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show bollinger bands
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

