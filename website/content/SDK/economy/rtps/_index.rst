.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get real-time performance sector data

    Returns
    -------
    df_sectors : *pd.Dataframe*
        Real-time performance data
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.rtps(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

 sector data

    
* **Returns**

    df_sectors : *pd.Dataframe*
        Real-time performance data
    