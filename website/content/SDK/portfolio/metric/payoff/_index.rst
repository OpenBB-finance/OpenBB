.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.payoff(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Gets payoff ratio

    Returns
    -------
    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods
    </p>

* **Returns**

    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods
