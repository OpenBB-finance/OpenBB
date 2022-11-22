.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.dividends(
    date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets dividend calendar for given date.  Date represents Ex-Dividend Date
    </p>

* **Parameters**

    date: datetime
        Date to get for in format YYYY-MM-DD

* **Returns**

    pd.DataFrame:
        Dataframe of dividend calendar
