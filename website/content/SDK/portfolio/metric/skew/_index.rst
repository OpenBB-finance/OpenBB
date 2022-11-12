.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.skew(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Method that retrieves skewness for portfolio and benchmark selected

    portfolio: PortfolioEngine
        PortfolioEngine object with trades loaded

    Returns
    -------
    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods
    </p>

* **Returns**

    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods
