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
stocks.gov.gtrades(
    symbol: str,
    gov_type: str = 'congress',
    past_transactions_months: int = 6,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Government trading for specific ticker [Source: quiverquant.com]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of tickers government trading

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.gtrades(
    symbol: str,
    gov_type: str = 'congress',
    past_transactions_months: int = 6,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Government trading for specific ticker [Source: quiverquant.com]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for
    raw: bool
        Show raw output of trades
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

