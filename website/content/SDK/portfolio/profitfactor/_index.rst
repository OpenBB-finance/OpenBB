.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets profit factor
    </h3>

{{< highlight python >}}
portfolio.profitfactor(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel
)
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods
    