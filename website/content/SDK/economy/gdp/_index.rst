.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get annual or quarterly Real GDP for US
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.gdp(
    interval: str = 'q',
    start_year: int = 2010,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    interval : str, optional
        Interval for GDP, by default "a" for annual, by default "q"
    start_year : int, optional
        Start year for plot, by default 2010
    
* **Returns**

    pd.DataFrame
        Dataframe of GDP
    