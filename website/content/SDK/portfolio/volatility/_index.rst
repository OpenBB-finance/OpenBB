.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.volatility(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Class method that retrieves volatility for portfolio and benchmark selected
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame with volatility for portfolio and benchmark for different periods
