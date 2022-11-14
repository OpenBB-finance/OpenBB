.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.var(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 99.9,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get portfolio VaR
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    use_mean: bool
        if one should use the data mean return
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: float
        var percentile (%)

* **Returns**

    pd.DataFrame
        DataFrame with portfolio VaR

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.var(P)
    {{< /highlight >}}
