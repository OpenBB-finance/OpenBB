.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.sortino(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    risk_free_rate: float = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Method that retrieves sortino ratio for portfolio and benchmark selected
    </p>

* **Parameters**

    portfolio: PortfolioEngine
        PortfolioEngine object with trades loaded
    risk_free_rate: float
        Risk free rate value

* **Returns**

    pd.DataFrame
        DataFrame with sortino ratio for portfolio and benchmark for different periods
