.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get full option chains with calculated greeks
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.chains_yf(
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls: bool = True,
    puts: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol
    expiry: *str*
        Expiration date for chain in format YYY-mm-dd
    calls: *bool*
        Flag to get calls
    puts: *bool*
        Flag to get puts

    
* **Returns**

    pd.DataFrame
        DataFrame of option chain.  If both calls and puts
   