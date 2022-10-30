.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get portfolio VaR
    </h3>

{{< highlight python >}}
portfolio.var(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, use\_mean: bool = False,
    adjusted\_var: bool = False,
    student\_t: bool = False,
    percentile: float = 99.9,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    use\_mean: *bool*
        if one should use the data mean return
    adjusted\_var: *bool*
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student\_t: *bool*
        If one should use the student-t distribution
    percentile: *float*
        var percentile (%)
    
* **Returns**

    pd.DataFrame

    