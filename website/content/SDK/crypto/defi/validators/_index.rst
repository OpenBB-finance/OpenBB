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
crypto.defi.validators(
    sortby: str = 'votingPower',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get information about terra validators [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    sortby: str
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: bool
        Flag to sort data descending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        terra validators details

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.validators(
    limit: int = 10,
    sortby: str = 'votingPower',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display information about terra validators [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

