.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.skew(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Class method that retrieves skewness for portfolio and benchmark selected

    portfolio: Portfolio
        Portfolio object with trades loaded

    Returns
    -------
    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods
    </p>

* **Returns**

    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods
