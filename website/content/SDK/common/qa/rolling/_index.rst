.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return rolling mean and standard deviation
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.rolling(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of target data
    window: *int*
        Length of rolling window

    
* **Returns**

    pd.DataFrame:
        Dataframe of rolling mean
    pd.DataFrame:
        Dataframe of rolling standard deviation
   