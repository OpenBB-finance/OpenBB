.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.sortino(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    risk_free_rate: float = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Class method that retrieves sortino ratio for portfolio and benchmark selected
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    risk_free_rate: float
        Risk free rate value

* **Returns**

    pd.DataFrame
        DataFrame with sortino ratio for portfolio and benchmark for different periods
