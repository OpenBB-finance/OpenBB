.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get government contracts for ticker [Source: quiverquant.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.contracts(
    symbol: str,
    past_transaction_days: int = 10,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to get congress trading data from
    past_transaction_days: *int*
        Number of days to get transactions for

    
* **Returns**

    pd.DataFrame
        Most recent transactions by members of U.S. Congress
    