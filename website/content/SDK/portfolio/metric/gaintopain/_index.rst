.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.gaintopain(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get Pain-to-Gain ratio based on historical data
    </p>

* **Parameters**

    portfolio: PortfolioEngine
        PortfolioEngine object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame of the portfolio's gain-to-pain ratio
