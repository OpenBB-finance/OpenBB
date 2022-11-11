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
stocks.dd.sec(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get SEC filings for a given stock ticker. [Source: Market Watch]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    chart: bool
       Flag to display chart


* **Returns**

    df_financials : pd.DataFrame
        SEC filings data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dd.sec(
    symbol: str,
    limit: int = 5,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display SEC filings for a given stock ticker. [Source: Market Watch]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    limit: int
        Number of ratings to display
    export: str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

