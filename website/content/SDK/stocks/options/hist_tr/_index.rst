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
stocks.options.hist_tr(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    chain_id: Optional[str] = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets historical option pricing.  This inputs either ticker, expiration, strike or the OCC chain ID and processes
    the request to tradier for historical premiums.
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration date
    strike: int
        Option strike price
    put: bool
        Is this a put option?
    chain_id: Optional[str]
        OCC chain ID
    chart: bool
       Flag to display chart


* **Returns**

    df_hist: pd.DataFrame
        Dataframe of historical option prices

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.hist_tr(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    raw: bool = False,
    chain_id: str = None,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot historical option prices
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    expiry: str
        Expiry date of option
    strike: float
        Option strike price
    put: bool
        Is this a put option?
    raw: bool
        Print raw data
    chain_id: str
        OCC option symbol
    export: str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

