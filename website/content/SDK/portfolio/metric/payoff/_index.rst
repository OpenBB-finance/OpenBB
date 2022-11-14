.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.payoff(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Gets payoff ratio

    Returns
    -------
    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.payoff(P)
    </p>

* **Returns**

    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.payoff(P)
    {{< /highlight >}}
