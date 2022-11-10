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
common.qa.quantile(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    quantile_pct: float = 0.5,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Overlay Median & Quantile
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of targeted data
    window : int
        Length of window
    quantile_pct: float
        Quantile to display
    chart: bool
       Flag to display chart


* **Returns**

    df_med : pd.DataFrame
        Dataframe of median prices over window
    df_quantile : pd.DataFrame
        Dataframe of gievn quantile prices over window

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.quantile(
    data: pandas.core.frame.DataFrame,
    target: str,
    symbol: str = '',
    window: int = 14,
    quantile: float = 0.5,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    View rolling quantile
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    symbol : str
        Stock ticker
    window : int
        Length of window
    quantile: float
        Quantile to get
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

