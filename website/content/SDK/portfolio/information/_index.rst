.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get information ratio
    </h3>

{{< highlight python >}}
portfolio.information(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
)
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

* **Returns**

    pd.DataFrame
        DataFrame of the information ratio during different time periods
