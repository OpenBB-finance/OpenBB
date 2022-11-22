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
stocks.gov.contracts(
    symbol: str,
    past_transaction_days: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get government contracts for ticker [Source: quiverquant.com]
    </p>

* **Parameters**

    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Most recent transactions by members of U.S. Congress

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.contracts(
    symbol: str,
    past_transaction_days: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show government contracts for ticker [Source: quiverquant.com]
    </p>

* **Parameters**

    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

