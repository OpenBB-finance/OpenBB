.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Government trading for specific ticker [Source: quiverquant.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.gtrades(
    symbol: str,
    gov\_type: str = 'congress',
    past\_transactions\_months: int = 6,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get congress trading data from
    gov_type: *str*
        Type of government data between: congress, senate and house
    past_transactions_months: *int*
        Number of months to get transactions for

    
* **Returns**

    pd.DataFrame
        DataFrame of tickers government trading
    