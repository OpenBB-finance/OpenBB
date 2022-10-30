.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get information about terra validators [Source: https://fcd.terra.dev/swagger]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.validators(
    sortby: str = 'votingPower',
    ascend: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby: *str*
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: *bool*
        Flag to sort data descending

    
* **Returns**

    pd.DataFrame
        terra validators details
    