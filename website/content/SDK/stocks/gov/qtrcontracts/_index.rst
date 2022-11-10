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
stocks.gov.qtrcontracts(
    analysis: str = 'total',
    limit: int = 5,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Analyzes quarterly contracts by ticker
    </p>

* **Parameters**

    analysis : str
        How to analyze.  Either gives total amount or sorts by high/low momentum.
    limit : int, optional
        Number to return, by default 5
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe with tickers and total amount if total selected.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.qtrcontracts(
    analysis: str = 'total',
    limit: int = 5,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Quarterly contracts [Source: quiverquant.com]
    </p>

* **Parameters**

    analysis: str
        Analysis to perform.  Either 'total', 'upmom' 'downmom'
    limit: int
        Number to show
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

