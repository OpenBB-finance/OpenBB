.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.om(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get omega ratio
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.om(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display omega ratio
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    chart: bool
       Flag to display chart

