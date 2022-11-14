.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.es(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    use_mean: bool = False,
    distribution: str = 'normal',
    percentile: float = 99.9,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get portfolio expected shortfall
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    use_mean:
        if one should use the data mean return
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: float
        es percentile (%)

* **Returns**

    pd.DataFrame
        DataFrame with portfolio expected shortfall

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.es(P)
    {{< /highlight >}}
