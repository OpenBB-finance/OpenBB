.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets dividend calendar for given date.  Date represents Ex-Dividend Date
    </h3>

{{< highlight python >}}
stocks.disc.dividends(
    date: str = '2022-10-31', ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    date: *datetime*
        Date to get for in format YYYY-MM-DD

    
* **Returns**

    pd.DataFrame:
        Dataframe of dividend calendar
    