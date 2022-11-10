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
stocks.ta.rsp(
    s_ticker: str = '',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Relative strength percentile [Source: https://github.com/skyte/relative-strength]
    Currently takes from https://github.com/soggyomelette/rs-log in order to get desired output
    </p>

* **Parameters**

    s_ticker : str
        Stock Ticker
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of stock percentile
    pd.Dataframe
        Dataframe of industry percentile
    pd.Dataframe
        Raw stock dataframe for export
    pd.Dataframe
        Raw industry dataframe for export

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ta.rsp(
    s_ticker: str = '',
    export: str = '',
    tickers_show: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Relative Strength Percentile [Source: https://github.com/skyte/relative-strength]
    </p>

* **Parameters**

    s_ticker : str
        Stock ticker
    export : str
        Format of export file
    tickers_show : bool
        Boolean to check if tickers in the same industry as the stock should be shown
    chart: bool
       Flag to display chart

