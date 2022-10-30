.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Standard Deviation and Variance
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.spread(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        DataFrame of targeted data
    window: *int*
        Length of window

    
* **Returns**

    df_sd: *pd.DataFrame*
        Dataframe of rolling standard deviation
    df_var: *pd.DataFrame*
        Dataframe of rolling standard deviation
    