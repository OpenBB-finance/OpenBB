.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get supply history of the Terra ecosystem

    Source: [Smartstake.io]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.luna_supply(
    supply_type: str = 'lunaSupplyChallengeStats',
    days: int = 30,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    supply_type: *str*
        Supply type to unpack json
    days: *int*
        Day count to fetch data

    
* **Returns**

    pd.DataFrame
        Dataframe of supply history data
    