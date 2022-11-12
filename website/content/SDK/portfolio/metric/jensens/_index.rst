.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.jensens(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = '1y',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get jensen's alpha
    </p>

* **Parameters**

    portfolio: PortfolioEngine
        PortfolioEngine object with trades loaded
    window: str
        Interval used for rolling values
    risk_free_rate: float
        Risk free rate

* **Returns**

    pd.DataFrame
        DataFrame of jensens's alpha during different time windows
    pd.Series
        Series of jensens's alpha data
