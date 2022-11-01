.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.sratio(
    limit: int = 200,
    chart: bool = False
)
{{< /highlight >}}

* **Parameters**

    limit: *int*
        The number of ratios to show

    
* **Returns**

    pd.DataFrame
        historical staking ratio
    