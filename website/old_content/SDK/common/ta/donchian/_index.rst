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
common.ta.donchian(
    data: pandas.core.frame.DataFrame,
    upper_length: int = 20,
    lower_length: int = 20,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate Donchian Channels
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of ohlc prices
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of upper and lower channels

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.donchian(
    data: pandas.core.frame.DataFrame,
    symbol: str = '',
    upper_length: int = 20,
    lower_length: int = 20,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show donchian channels
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

