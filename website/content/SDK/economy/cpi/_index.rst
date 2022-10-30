.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get Consumer Price Index from Alpha Vantage
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.cpi(
    interval: str = 'm',
    start\_year: int = 2010,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    interval : *str*
        Interval for data.  Either "m" or "s" for monthly or semiannual
    start\_year : int, optional
        Start year for plot, by default 2010

    
* **Returns**

    pd.DataFrame
        Dataframe of CPI
    