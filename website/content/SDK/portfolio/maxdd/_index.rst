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
portfolio.maxdd(
    portfolio_engine: openbb_terminal.portfolio.portfolio_engine.PortfolioEngine,
    is_returns: bool = False,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.series.Series]
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate the drawdown (MDD) of historical series.  Note that the calculation is done
     on cumulative returns (or prices).  The definition of drawdown is

     DD = (current value - rolling maximum) / rolling maximum
    </p>

* **Parameters**

    data: pd.Series
        Series of input values
    is_returns: bool
        Flag to indicate inputs are returns
    chart: bool
       Flag to display chart


* **Returns**

    pd.Series
        Holdings series
    pd.Series
        Drawdown series

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> output = openbb.portfolio.maxdd(p)
    {{< /highlight >}}

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.maxdd(
    portfolio_engine: openbb_terminal.portfolio.portfolio_engine.PortfolioEngine,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display maximum drawdown curve
    </p>

* **Parameters**

    portfolio : PortfolioEngine
        PortfolioEngine object
    export: str
        Format to export data
    external_axes: plt.Axes
        Optional axes to display plot on
    chart: bool
       Flag to display chart

