.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical quarterly government contracts [Source: quiverquant.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.histcont(
    symbol: str,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get congress trading data from

    
* **Returns**

    pd.DataFrame
        Historical quarterly government contracts
    