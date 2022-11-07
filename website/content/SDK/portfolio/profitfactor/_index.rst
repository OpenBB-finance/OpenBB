.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.profitfactor(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Gets profit factor
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods
