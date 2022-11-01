.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.gov_proposals(
    status: str = '',
    sortby: str = 'id',
    ascend: bool = True,
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    status: *str*
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending
    limit: *int*
        Number of records to display

    
* **Returns**

    pd.DataFrame
        Terra blockchain governance proposals list
    