.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets kelly criterion
    </h3>

{{< highlight python >}}
portfolio.kelly(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    )
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame of kelly criterion of the portfolio during different time periods
    