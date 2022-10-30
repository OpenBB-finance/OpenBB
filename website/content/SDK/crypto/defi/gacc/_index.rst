.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.gacc(
    cumulative: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    cumulative: *bool*
        distinguish between periodical and cumulative account growth data
    
* **Returns**

    pd.DataFrame
        historical data of accounts growth
    