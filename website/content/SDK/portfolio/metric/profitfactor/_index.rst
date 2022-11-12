.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.profitfactor(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Gets profit factor
    </p>

* **Parameters**

    portfolio: PortfolioEngine
        PortfolioEngine object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods
