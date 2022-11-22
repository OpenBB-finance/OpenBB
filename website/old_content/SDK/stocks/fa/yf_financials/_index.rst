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
stocks.fa.yf_financials(
    symbol: str,
    statement: str,
    ratios: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get cashflow statement for company
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    statement: str
        can be:

        - cash-flow
        - financials for Income
        - balance-sheet

    ratios: bool
        Shows percentage change
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of Financial statement

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.fa.yf_financials(
    symbol: str,
    statement: str,
    limit: int = 12,
    ratios: bool = False,
    plot: list = None,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display tickers balance sheet, income statement or cash-flow
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    statement: str
        Possible values are:

        - cash-flow
        - financials for Income
        - balance-sheet

    limit: int
        Number of periods to show
    ratios: bool
        Shows percentage change
    plot: list
        List of row labels to plot
    export: str
        Format to export data
    chart: bool
       Flag to display chart

