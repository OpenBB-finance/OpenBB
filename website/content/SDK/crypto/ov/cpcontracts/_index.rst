.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets all contract addresses for given platform [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpcontracts(
    platform\_id: str = 'eth-ethereum', sortby: str = 'active',
    ascend: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    platform_id: *str*
        Blockchain platform like eth-ethereum
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascend

    
* **Returns**

    pandas.DataFrame
         id, type, active
    