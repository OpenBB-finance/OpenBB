.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.pr(
    main_coin: str,
    to_symbol: Optional[str] = None,
    limit: Optional[int] = None,
    price: Optional[int] = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    main_coin   : *str*
        Coin loaded to check potential returns for (e.g., algorand)
    to_symbol          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    limit         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)

    
* **Returns**

    pd.DataFrame
            Potential returns data
            Columns: Coin, Current Price, Target Coin, Potential Price, Potential Market Cap ($), Change (%)
    