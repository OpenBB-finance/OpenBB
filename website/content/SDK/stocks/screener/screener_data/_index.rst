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
stocks.screener.screener_data(
    preset_loaded: str = 'top_gainers',
    data_type: str = 'overview',
    limit: int = 10,
    ascend: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Screener Overview
    </p>

* **Parameters**

    preset_loaded : str
        Loaded preset filter
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical
    limit : int
        Limit of stocks filtered with presets to print
    ascend : bool
        Ascended order of stocks filtered to print
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe with loaded filtered stocks

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.screener.screener_data(
    loaded_preset: str = 'top_gainers',
    data_type: str = 'overview',
    limit: int = 10,
    ascend: bool = False,
    sortby: str = '',
    export: str = '',
    chart: bool = False,
) -> List[str]
{{< /highlight >}}

.. raw:: html

    <p>
    Screener one of the following: overview, valuation, financial, ownership, performance, technical.
    </p>

* **Parameters**

    loaded_preset: str
        Preset loaded to filter for tickers
    data_type : str
        Data type string between: overview, valuation, financial, ownership, performance, technical
    limit : int
        Limit of stocks to display
    ascend : bool
        Order of table to ascend or descend
    sortby: str
        Column to sort table by
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


* **Returns**

    List[str]
        List of stocks that meet preset criteria
