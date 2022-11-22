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
etf.etf_by_name(
    name_to_search: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]
    </p>

* **Parameters**

    name_to_search: str
        ETF name to match
    chart: bool
       Flag to display chart


* **Returns**

    df: pd.Dataframe
        Dataframe with symbols and names

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.etf_by_name(
    name: str,
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display ETFs matching search string. [Source: StockAnalysis]
    </p>

* **Parameters**

    name: str
        String being matched
    limit: int
        Limit of ETFs to display
    export: str
        Export to given file type
    chart: bool
       Flag to display chart

