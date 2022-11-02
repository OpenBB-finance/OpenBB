.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get tail ratio
    </h3>

{{< highlight python >}}
portfolio.tail(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    window: int = 252,
)
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    window: *int*
        Interval used for rolling values

* **Returns**

    pd.DataFrame
        DataFrame of the portfolios and the benchmarks tail ratio during different time windows
    pd.Series
        Series of the portfolios rolling tail ratio
    pd.Series
        Series of the benchmarks rolling tail ratio
