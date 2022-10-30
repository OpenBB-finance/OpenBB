.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets yield curve data from FRED
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.fred_yield_curve(
    date: datetime.datetime = None,
    chart: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, datetime.datetime]
{{< /highlight >}}

* **Parameters**

    date: *datetime*
        Date to get curve for.  If None, gets most recent date

    
* **Returns**

    pd.DataFrame:
        Dataframe of yields and maturities
    str
        Date for which the yield curve is obtained
    