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
crypto.onchain.ueat(
    interval: str = 'day',
    limit: int = 90,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get number of unique ethereum addresses which made a transaction in given time interval.
    </p>

* **Parameters**

    interval: str
        Time interval in which count unique ethereum addresses which made transaction. day,
        month or week.
    limit: int
        Number of records for data query.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Unique ethereum addresses which made a transaction

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.ueat(
    interval: str = 'days',
    limit: int = 10,
    sortby: str = 'date',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display number of unique ethereum addresses which made a transaction in given time interval
     [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    interval: str
        Time interval in which ethereum address made transaction. month, week or day
    limit: int
        Number of records to display. It's calculated base on provided interval.
        If interval is month then calculation is made in the way: limit * 30 = time period,
        in case if interval is set to week, then time period is calculated as limit * 7.
        For better user experience maximum time period in days is equal to 90.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Number of unique ethereum addresses which made a transaction in given time interval
