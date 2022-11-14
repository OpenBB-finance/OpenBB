.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.alloc.assets(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    tables: bool = False,
    limit: int = 10,
    recalculate: bool = False,
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]]
{{< /highlight >}}

.. raw:: html

    <p>
    Display portfolio asset allocation compared to the benchmark
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

* **Returns**

    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.alloc.assets(P)
    {{< /highlight >}}
