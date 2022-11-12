.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.rsquare(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Method that retrieves R2 Score for portfolio and benchmark selected
    </p>

* **Parameters**

    portfolio: PortfolioEngine
        PortfolioEngine object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame with R2 Score between portfolio and benchmark for different periods
