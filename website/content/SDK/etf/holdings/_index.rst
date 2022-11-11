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
etf.holdings(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get ETF holdings
    </p>

* **Parameters**

    symbol: str
        Symbol to get holdings for
    chart: bool
       Flag to display chart


* **Returns**

    df: pd.DataFrame
        Dataframe of holdings

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.holdings(
    symbol: str,
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    
    </p>

* **Parameters**

    symbol: str
        ETF symbol to show holdings for
    limit: int
        Number of holdings to show
    export: str
        Format to export data
    chart: bool
       Flag to display chart

