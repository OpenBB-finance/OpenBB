.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.trackerr(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    window: int = 252,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get tracking error
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    window: int
        Interval used for rolling values

* **Returns**

    pd.DataFrame
        DataFrame of tracking errors during different time windows
    pd.Series
        Series of rolling tracking error
