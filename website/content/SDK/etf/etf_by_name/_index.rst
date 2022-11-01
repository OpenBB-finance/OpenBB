.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.etf_by_name(
    name_to_search: str,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    name_to_search: *str*
        ETF name to match

    
* **Returns**

    df: *pd.Dataframe*
        Dataframe with symbols and names
    