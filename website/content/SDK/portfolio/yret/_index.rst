.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get yearly returns
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.yret(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    window: str = 'all',
    chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    window : *str*
        interval to compare cumulative returns and benchmark
   