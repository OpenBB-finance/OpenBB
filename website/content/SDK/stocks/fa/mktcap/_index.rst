.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get market cap over time for ticker. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.fa.mktcap(
    symbol: str,
    start_date: str = '2019-10-31',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to get market cap over time
    start_date: *str*
        Start date to display market cap

    
* **Returns**

    pd.DataFrame:
        Dataframe of estimated market cap over time
    str:
        Currency of ticker
    