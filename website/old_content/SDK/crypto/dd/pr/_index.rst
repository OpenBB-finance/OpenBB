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
crypto.dd.pr(
    main_coin: str,
    to_symbol: Optional[str] = None,
    limit: Optional[int] = None,
    price: Optional[int] = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]
    </p>

* **Parameters**

    main_coin   : str
        Coin loaded to check potential returns for (e.g., algorand)
    to_symbol          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    limit         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
            Potential returns data
            Columns: Coin, Current Price, Target Coin, Potential Price, Potential Market Cap ($), Change (%)

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.pr(
    to_symbol: str,
    from_symbol: Optional[str] = None,
    limit: Optional[int] = None,
    price: Optional[int] = None,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays potential returns of a certain coin. [Source: CoinGecko]
    </p>

* **Parameters**

    to_symbol   : str
        Coin loaded to check potential returns for (e.g., algorand)
    from_symbol          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    limit         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

