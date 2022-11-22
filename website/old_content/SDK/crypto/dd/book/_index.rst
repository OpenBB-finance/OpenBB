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
crypto.dd.book(
    from_symbol: str,
    limit: int = 100,
    to_symbol: str = 'USDT',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get order book for currency. [Source: Binance]
    </p>

* **Parameters**

    from_symbol: *str*
        Cryptocurrency symbol
    limit: *int*
        Limit parameter. Adjusts the weight
    to_symbol: *str*
        Quote currency (what to view coin vs)
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing orderbook

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.book(
    from_symbol: str,
    limit: int = 100,
    to_symbol: str = 'USDT',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get order book for currency. [Source: Binance]
    </p>

* **Parameters**

    from_symbol: *str*
        Cryptocurrency symbol
    limit: *int*
        Limit parameter. Adjusts the weight
    to_symbol: *str*
        Quote currency (what to view coin vs)
    export: *str*
        Export dataframe data to csv,json,xlsx
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    chart: *bool*
       Flag to display chart

