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
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Method that retrieves skewness for portfolio and benchmark selected

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods
    </p>

* **Returns**

    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods
