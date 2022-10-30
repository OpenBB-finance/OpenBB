.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get portfolio expected shortfall
    </h3>

{{< highlight python >}}
portfolio.es(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    use_mean: bool = False,
    distribution: str = 'normal',
    percentile: float = 99.9,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    use_mean:
        if one should use the data mean return
    distribution: *str*
        choose distribution to use: logistic, laplace, normal
    percentile: *float*
        es percentile (%)
    
* **Returns**

    pd.DataFrame

    