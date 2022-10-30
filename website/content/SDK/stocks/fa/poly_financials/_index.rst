.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get ticker financial statements from polygon
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.fa.poly_financials(
    symbol: str,
    statement: str,
    quarterly: bool = False,
    ratios: bool = False,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol
    statement: *str*
        Financial statement data to retrieve, can be balance, income or cash
    quarterly:bool
        Flag to get quarterly reports, by default False
    ratios: *bool*
        Shows percentage change, by default False

    
* **Returns**

    pd.DataFrame
        Balance Sheets or Income Statements
    