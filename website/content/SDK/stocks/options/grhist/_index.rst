.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get histoical option greeks
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.options.grhist(
    symbol: str,
    expiry: str,
    strike: float,
    chain_id: str = '',
    put: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol
    expiry: *str*
        Option expiration date
    strike: *float*
        Strike price to look for
    chain_id: *str*
        OCC option symbol.  Overwrites other inputs
    put: *bool*
        Is this a put option?
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    df: *pd.DataFrame*
        Dataframe containing historical greeks
