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
stocks.options.grhist(
    symbol: str,
    expiry: str,
    strike: Union[str, float],
    chain_id: str = '',
    put: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get histoical option greeks
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration date
    strike: Union[str, float]
        Strike price to look for
    chain_id: str
        OCC option symbol.  Overwrites other inputs
    put: bool
        Is this a put option?
    chart: bool
       Flag to display chart


* **Returns**

    df: pd.DataFrame
        Dataframe containing historical greeks

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.grhist(
    symbol: str,
    expiry: str,
    strike: Union[float, str],
    greek: str = 'Delta',
    chain_id: str = '',
    put: bool = False,
    raw: bool = False,
    limit: Union[int, str] = 20,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plots historical greeks for a given option. [Source: Syncretism]
    </p>

* **Parameters**

    symbol: str
        Stock ticker
    expiry: str
        Expiration date
    strike: Union[str, float]
        Strike price to consider
    greek: str
        Greek variable to plot
    chain_id: str
        OCC option chain.  Overwrites other variables
    put: bool
        Is this a put option?
    raw: bool
        Print to console
    limit: int
        Number of rows to show in raw
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

