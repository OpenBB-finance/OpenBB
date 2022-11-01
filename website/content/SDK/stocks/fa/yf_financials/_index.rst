.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get cashflow statement for company
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.fa.yf_financials(
    symbol: str,
    statement: str,
    ratios: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol
    statement: *str*
        can be:
            cash-flow
            financials for Income
            balance-sheet
    ratios: *bool*
        Shows percentage change

    
* **Returns**

    pd.DataFrame
        Dataframe of Financial statement
    