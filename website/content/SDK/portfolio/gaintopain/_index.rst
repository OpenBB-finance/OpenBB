.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get Pain-to-Gain ratio based on historical data
    </h3>

{{< highlight python >}}
portfolio.gaintopain(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    )
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame of the portfolio's gain-to-pain ratio
    