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
crypto.ov.cr(
    rate_type: str = 'borrow',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]
    </p>

* **Parameters**

    rate_type : str
        Interest rate type: {borrow, supply}. Default: supply
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame: crypto interest rates per platform

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cr(
    symbols: str,
    platforms: str,
    rate_type: str = 'borrow',
    limit: int = 10,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]
    </p>

* **Parameters**

    rate_type: str
        Interest rate type: {borrow, supply}. Default: supply
    symbols: str
        Crypto separated by commas. Default: BTC,ETH,USDT,USDC
    platforms: str
        Platforms separated by commas. Default: BlockFi,Ledn,SwissBorg,Youhodler
    limit: int
        Number of records to show
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

