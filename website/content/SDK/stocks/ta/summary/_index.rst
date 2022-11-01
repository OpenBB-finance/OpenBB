.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get technical summary report provided by FinBrain's API
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ta.summary(
    symbol: str,
    chart: bool = False,
) -> str
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol to get the technical summary

    
* **Returns**

    report:str
        technical summary report
    