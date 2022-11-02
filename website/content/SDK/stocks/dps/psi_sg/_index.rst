.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get price vs short interest volume. [Source: Stockgrid]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dps.psi_sg(
    symbol: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, List]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock to get data from

    
* **Returns**

    pd.DataFrame
        Short interest volume data
    List
        Price data
   