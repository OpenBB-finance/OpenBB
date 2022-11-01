.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get overview data for selected etf
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.overview(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    etf_symbol : *str*
        Etf symbol to get overview for

    
* **Returns**

    df : *pd.DataFrame*
        Dataframe of stock overview data
    