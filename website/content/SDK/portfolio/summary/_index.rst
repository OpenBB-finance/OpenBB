.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.summary(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    window: str = 'all',
    risk_free_rate: float = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get summary portfolio and benchmark returns
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations

* **Returns**

    pd.DataFrame
