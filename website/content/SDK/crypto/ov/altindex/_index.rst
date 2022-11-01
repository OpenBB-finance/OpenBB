.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get altcoin index overtime
    [Source: https://blockchaincenter.net]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.altindex(
    period: int = 30,
    start_date: int = 1262304000,
    end_date: int = 1667297196,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    period: *int*
       Number of days {30,90,365} to check performance of coins and calculate the altcoin index.
       E.g., 365 checks yearly performance, 90 will check seasonal performance (90 days),
       30 will check monthly performance (30 days).
    start_date : *int*
        Initial date timestamp (e.g., 1_609_459_200)
    end_date : *int*
        End date timestamp (e.g., 1_641_588_030)

    
* **Returns**

    pandas.DataFrame:
        Date, Value (Altcoin Index)
    