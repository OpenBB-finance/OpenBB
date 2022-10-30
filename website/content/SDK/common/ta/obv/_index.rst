.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > On Balance Volume
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.obv(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of OHLC prices

    
* **Returns**

    pd.DataFrame
        Dataframe with technical indicator
    