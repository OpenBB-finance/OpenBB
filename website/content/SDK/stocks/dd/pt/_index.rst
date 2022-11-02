.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get analysts' price targets for a given stock. [Source: Business Insider]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dd.pt(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol

    
* **Returns**

    pd.DataFrame
        Analysts data
   