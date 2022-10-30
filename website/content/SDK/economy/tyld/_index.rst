.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical yield for a given maturity
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.tyld(
    interval: str = 'm',
    maturity: str = '10y',
    start\_date: str = '2010-01-01', chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    interval : *str*
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    start\_date: *str*
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    maturity : *str*
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"

    
* **Returns**

    pd.DataFrame
        Dataframe of historical yields
    