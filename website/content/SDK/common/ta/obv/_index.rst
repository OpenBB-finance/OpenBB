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
common.ta.obv(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    On Balance Volume
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of OHLC prices
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe with technical indicator

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.obv(
    data: pandas.core.frame.DataFrame,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot OBV technical indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker
    export: str
        Format to export data as
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

