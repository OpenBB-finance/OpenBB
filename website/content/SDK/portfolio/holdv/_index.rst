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
portfolio.holdv(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get holdings of assets (absolute value)
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of holdings

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.holdv(P)
    {{< /highlight >}}

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.holdv(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
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
    Display holdings of assets (absolute value)
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
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

