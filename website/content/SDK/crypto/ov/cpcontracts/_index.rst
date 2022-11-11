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
crypto.ov.cpcontracts(
    platform_id: str = 'eth-ethereum',
    sortby: str = 'active',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets all contract addresses for given platform [Source: CoinPaprika]
    </p>

* **Parameters**

    platform_id: str
        Blockchain platform like eth-ethereum
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
         id, type, active

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cpcontracts(
    symbol: str,
    sortby: str = 'active',
    ascend: bool = True,
    limit: int = 15,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Gets all contract addresses for given platform. [Source: CoinPaprika]
    </p>

* **Parameters**

    platform: str
        Blockchain platform like eth-ethereum
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

