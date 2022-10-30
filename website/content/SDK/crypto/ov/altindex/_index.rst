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
    start\_date: int = 1262304000,
    end\_date: int = 1667172037,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    period: *int*
       Number of days {30,90,365} to check performance of coins and calculate the altcoin index.
       E.g., 365 checks yearly performance, 90 will check seasonal performance (90 days),
       30 will check monthly performance (30 days).
    start\_date : *int*
        Initial date timestamp (e.g., 1\_609\_459\_200)
    end\_date : *int*
        End date timestamp (e.g., 1\_641\_588\_030)

    
* **Returns**

    pandas.DataFrame:
        Date, Value (Altcoin Index)
    