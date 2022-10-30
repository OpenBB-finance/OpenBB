.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get IPO calendar
    </h3>

{{< highlight python >}}
stocks.disc.ipo(
    start_date: str = '2022-10-25', end_date: str = '2022-10-30', ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    start_date : *str*
        start date (%Y-%m-%d) to get IPO calendar
    end_date : *str*
        end date (%Y-%m-%d) to get IPO calendar

    
* **Returns**

    pd.DataFrame
        Get dataframe with economic calendar events
    