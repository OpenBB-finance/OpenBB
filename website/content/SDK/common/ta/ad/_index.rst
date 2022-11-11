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
common.ta.ad(
    data: pandas.core.frame.DataFrame,
    use_open: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate AD technical indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of prices with OHLC and Volume
    use_open : bool
        Whether to use open prices
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
common.ta.ad(
    data: pandas.core.frame.DataFrame,
    use_open: bool = False,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot AD technical indicator
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    symbol : str
        Ticker symbol
    export: str
        Format to export data as
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

