.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Class method that retrieves volatility for portfolio and benchmark selected
    </h3>

{{< highlight python >}}
portfolio.volatility(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame with volatility for portfolio and benchmark for different periods
