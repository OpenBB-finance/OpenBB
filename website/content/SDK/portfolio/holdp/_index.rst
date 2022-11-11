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
portfolio.holdp(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get holdings of assets (in percentage)
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.holdp(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    unstack: bool = False,
    raw: bool = False,
    limit: int = 10,
    export: str = '',
    external_axes: Optional[matplotlib.axes._axes.Axes] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display holdings of assets (in percentage)
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    unstack: bool
        Individual assets over time
    raw : bool
        To display raw data
    limit : int
        Number of past market days to display holdings
    export: str
        Format to export plot
    external_axes: plt.Axes
        Optional axes to display plot on
    chart: bool
       Flag to display chart

