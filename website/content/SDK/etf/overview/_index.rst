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
etf.overview(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get overview data for selected etf
    </p>

* **Parameters**

    etf_symbol : str
        Etf symbol to get overview for
    chart: bool
       Flag to display chart


* **Returns**

    df : pd.DataFrame
        Dataframe of stock overview data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.overview(
    symbol: str,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print etf overview information
    </p>

* **Parameters**

    symbol:str
        ETF symbols to display overview for
    export:str
        Format to export data
    chart: bool
       Flag to display chart

