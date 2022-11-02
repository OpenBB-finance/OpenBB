.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Government trading for specific ticker [Source: quiverquant.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.gov.gtrades(
    symbol: str,
    gov_type: str = 'congress',
    past_transactions_months: int = 6,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get congress trading data from
    gov_type: *str*
        Type of government data between: congress, senate and house
    past_transactions_months: *int*
        Number of months to get transactions for
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        DataFrame of tickers government trading
