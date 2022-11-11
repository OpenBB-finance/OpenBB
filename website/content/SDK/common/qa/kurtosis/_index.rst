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
common.qa.kurtosis(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Kurtosis Indicator
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of targeted data
    window: int
        Length of window
    chart: bool
       Flag to display chart


* **Returns**

    df_kurt : pd.DataFrame
        Dataframe of rolling kurtosis

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.kurtosis(
    symbol: str,
    data: pandas.core.frame.DataFrame,
    target: str,
    window: int = 14,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    View rolling kurtosis
    </p>

* **Parameters**

    symbol: str
        Ticker
    data: pd.DataFrame
        Dataframe of stock prices
    target: str
        Column in data to look at
    window: int
        Length of window
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

