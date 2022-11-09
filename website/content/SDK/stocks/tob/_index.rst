.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.tob(
    symbol: str,
    exchange: str = 'BZX',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Get top of book bid and ask for ticker on exchange [CBOE.com]
    </p>

* **Parameters**

    symbol: str
        Ticker to get
    exchange: str
        Exchange to look at.  Can be `BZX`,`EDGX`, `BYX`, `EDGA`

* **Returns**

    pd.DatatFrame
        Dataframe of Bids
    pd.DataFrame
        Dataframe of asks
