.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get histoical option greeks
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.grhist(
    symbol: str,
    expiry: str,
    strike: float,
    chain_id: str = '',
    put: bool = False,
    chart: bool = False
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

    
* **Returns**

    df: *pd.DataFrame*
        Dataframe containing historical greeks
    