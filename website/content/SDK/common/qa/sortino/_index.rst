.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculates the sortino ratio
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.sortino(
    data: pandas.core.frame.DataFrame,
    target_return: float = 0,
    window: float = 252,
    adjusted: bool = False,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        selected dataframe
    target_return: *float*
        target return of the asset
    window: *float*
        length of the rolling window
    adjusted: *bool*
        adjust the sortino ratio

    
* **Returns**

    sortino: *pd.DataFrame*
        sortino ratio
    