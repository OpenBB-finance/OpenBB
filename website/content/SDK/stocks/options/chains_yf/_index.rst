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

.. raw:: html

    <p>
    Get full option chains with calculated greeks
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration date for chain in format YYY-mm-dd
    calls: bool
        Flag to get calls
    puts: bool
        Flag to get puts
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of option chain.  If both calls and puts

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.chains_yf(
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display option chains for given ticker and expiration
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration for option chain
    min_sp: float
        Min strike
    max_sp: float
        Max strike
    calls_only: bool
        Flag to get calls only
    puts_only: bool
        Flag to get puts only
    export: str
        Format to export data
    chart: bool
       Flag to display chart

