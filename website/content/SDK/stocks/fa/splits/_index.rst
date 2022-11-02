.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get splits and reverse splits events. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.fa.splits(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to get forward and reverse splits

    
* **Returns**

    pd.DataFrame:
        Dataframe of forward and reverse splits
   