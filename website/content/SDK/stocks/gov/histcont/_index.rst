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
stocks.gov.histcont(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical quarterly government contracts [Source: quiverquant.com]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get congress trading data from
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Historical quarterly government contracts

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.histcont(
    symbol: str,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show historical quarterly government contracts [Source: quiverquant.com]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get congress trading data from
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

