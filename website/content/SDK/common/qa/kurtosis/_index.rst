.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Kurtosis Indicator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.kurtosis(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of targeted data
    window: *int*
        Length of window

    
* **Returns**

    df_kurt : *pd.DataFrame*
        Dataframe of rolling kurtosis
    