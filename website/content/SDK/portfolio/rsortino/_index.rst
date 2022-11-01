.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get rolling sortino
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.rsortino(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    risk_free_rate: float = 0,
    window: str = '1y',
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio : *PortfolioModel*
        Portfolio object
    window: *str*
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y
    risk_free_rate: *float*
        Value to use for risk free rate in sharpe/other calculations
    
* **Returns**

    pd.DataFrame
        Rolling sortino ratio DataFrame
    