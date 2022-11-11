.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.calmar(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    window: int = 756,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get calmar ratio
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    window: int
        Interval used for rolling values

* **Returns**

    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data
