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
    main\_coin: str,
    to\_symbol: Optional[str] = None,
    limit: Optional[int] = None,
    price: Optional[int] = None,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    main\_coin   : *str*
        Coin loaded to check potential returns for (e.g., algorand)
    to\_symbol          : str | None
        Coin to compare main\_coin with (e.g., bitcoin)
    limit         : int | None
        Number of coins with highest market cap to compare main\_coin with (e.g., 5)
    price
        Target price of main\_coin to check potential returns (e.g., 5)

    
* **Returns**

    pd.DataFrame
            Potential returns data
            Columns: Coin, Current Price, Target Coin, Potential Price, Potential Market Cap ($), Change (%)
    