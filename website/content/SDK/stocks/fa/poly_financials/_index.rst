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
stocks.fa.poly_financials(
    symbol: str,
    statement: str,
    quarterly: bool = False,
    ratios: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get ticker financial statements from polygon
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    statement: str
        Financial statement data to retrieve, can be balance, income or cash
    quarterly:bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Balance Sheets or Income Statements

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.fa.poly_financials(
    symbol: str,
    statement: str,
    limit: int = 10,
    quarterly: bool = False,
    ratios: bool = False,
    plot: list = None,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display tickers balance sheet or income statement
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    statement:str
        Either balance or income
    limit: int
        Number of results to show, by default 10
    quarterly: bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    export: str
        Format to export data
    chart: bool
       Flag to display chart

