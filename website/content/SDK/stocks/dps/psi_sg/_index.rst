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
stocks.dps.psi_sg(
    symbol: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, List]
{{< /highlight >}}

.. raw:: html

    <p>
    Get price vs short interest volume. [Source: Stockgrid]
    </p>

* **Parameters**

    symbol : str
        Stock to get data from
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Short interest volume data
    List
        Price data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dps.psi_sg(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot price vs short interest volume. [Source: Stockgrid]
    </p>

* **Parameters**

    symbol : str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

