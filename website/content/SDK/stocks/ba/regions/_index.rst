.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get interest by region from google api [Source: google]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.regions(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to look at

    
* **Returns**

    pd.DataFrame
        Dataframe of interest by region
   