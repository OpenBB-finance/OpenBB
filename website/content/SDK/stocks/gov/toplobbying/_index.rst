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
stocks.gov.toplobbying() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Corporate lobbying details
    </p>

* **Returns**

    pd.DataFrame
        DataFrame of top corporate lobbying

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.toplobbying(
    limit: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Top lobbying tickers based on total spent
    </p>

* **Parameters**

    limit: int
        Number of tickers to show
    raw: bool
        Show raw data
    export:
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

