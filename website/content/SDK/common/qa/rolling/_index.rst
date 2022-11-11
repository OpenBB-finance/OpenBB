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
common.qa.rolling(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Return rolling mean and standard deviation
    </p>

* **Parameters**

    data: pd.DataFrame
        Dataframe of target data
    window: int
        Length of rolling window
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        Dataframe of rolling mean
    pd.DataFrame:
        Dataframe of rolling standard deviation

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.rolling(
    data: pandas.core.frame.DataFrame,
    target: str,
    symbol: str = '',
    window: int = 14,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    View mean std deviation
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
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

