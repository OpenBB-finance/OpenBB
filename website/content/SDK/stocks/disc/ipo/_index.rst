.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.ipo(
    start_date: str = '2022-11-05',
    end_date: str = '2022-11-10',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get IPO calendar
    </p>

* **Parameters**

    start_date : str
        start date (%Y-%m-%d) to get IPO calendar
    end_date : str
        end date (%Y-%m-%d) to get IPO calendar

* **Returns**

    pd.DataFrame
        Get dataframe with economic calendar events
