.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets put call ratio over last time window [Source: AlphaQuery.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.pcr(
    symbol: str,
    window: int = 30,
    start_date: str = '2021-11-01',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to look for
    window: int, optional
        Window to consider, by default 30
    start_date: str, optional
        Start date to plot, by default last 366 days
   