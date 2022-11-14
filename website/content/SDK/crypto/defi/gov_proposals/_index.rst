.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.defi.gov_proposals(
    status: str = '',
    sortby: str = 'id',
    ascend: bool = True,
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    limit: int
        Number of records to display
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Terra blockchain governance proposals list

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.gov_proposals(
    limit: int = 10,
    status: str = 'all',
    sortby: str = 'id',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

