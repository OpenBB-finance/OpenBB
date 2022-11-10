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
stocks.options.hist_ce(
    symbol: str = 'GME',
    date: str = '2021-02-05',
    call: bool = True,
    price: str = '90',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Historic prices for a specific option [chartexchange]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get historical data from
    date : str
        Date as a string YYYYMMDD
    call : bool
        Whether to show a call or a put
    price : str
        Strike price for a specific option
    chart: bool
       Flag to display chart


* **Returns**

    historical : pd.Dataframe
        Historic information for an option

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.hist_ce(
    symbol: str = 'GME',
    expiry: str = '2021-02-05',
    call: bool = True,
    price: float = 90,
    limit: int = 10,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Return raw stock data[chartexchange]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol for the given option
    expiry : str
        The expiry of expiration, format "YYYY-MM-DD", i.e. 2010-12-31.
    call : bool
        Whether the underlying asset should be a call or a put
    price : float
        The strike of the expiration
    limit : int
        Number of rows to show
    export : str
        Export data as CSV, JSON, XLSX
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

