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
stocks.options.vsurf(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets IV surface for calls and puts for ticker
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol to get
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of DTE, Strike and IV

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.vsurf(
    symbol: str,
    export: str = '',
    z: str = 'IV',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display vol surface
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get surface for
    export : str
        Format to export data
    z : str
        The variable for the Z axis
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

