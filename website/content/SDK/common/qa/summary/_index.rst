.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Print summary statistics
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.summary(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Dataframe to get summary statistics for

    
* **Returns**

    summary : *pd.DataFrame*
        Summary statistics
   