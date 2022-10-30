.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get holdings of assets (in percentage)
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.holdp(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    