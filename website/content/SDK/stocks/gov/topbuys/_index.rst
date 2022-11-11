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
stocks.gov.topbuys(
    gov_type: str = 'congress',
    past_transactions_months: int = 6,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get top buy government trading [Source: quiverquant.com]
    </p>

* **Parameters**

    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of top government buy trading

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.topbuys(
    gov_type: str = 'congress',
    past_transactions_months: int = 6,
    limit: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Top buy government trading [Source: quiverquant.com]
    </p>

* **Parameters**

    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    limit: int
        Number of tickers to show
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

