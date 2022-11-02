.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get rolling sharpe ratio
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.rsharpe(
    portfolio: pandas.core.frame.DataFrame,
    risk_free_rate: float = 0,
    window: str = '1y',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio_returns : *pd.Series*
        Series of portfolio returns
    risk_free_rate : *float*
        Risk free rate
    window : *str*
        Rolling window to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

    
* **Returns**

    pd.DataFrame
        Rolling sharpe ratio DataFrame
   