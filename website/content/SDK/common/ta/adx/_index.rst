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
common.ta.adx(
    high_values: pandas.core.series.Series,
    low_values: pandas.core.series.Series,
    close_values: pandas.core.series.Series,
    window: int = 14,
    scalar: int = 100,
    drift: int = 1,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    ADX technical indicator
    </p>

* **Parameters**

    high_values: *pd.Series*
        High prices
    low_values: *pd.Series*
        Low prices
    close_values: *pd.Series*
        close prices
    window: *int*
        Length of window
    scalar: *int*
        Scalar variable
    drift: *int*
        Drift variable
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame with adx indicator

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.adx(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    scalar: int = 100,
    drift: int = 1,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot ADX indicator
    </p>

* **Parameters**

    data : *pd.DataFrame*
        Dataframe with OHLC price data
    window : *int*
        Length of window
    scalar : *int*
        Scalar variable
    drift : *int*
        Drift variable
    symbol : *str*
        Ticker
    export : *str*
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: *bool*
       Flag to display chart

