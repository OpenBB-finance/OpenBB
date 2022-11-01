.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Real GDP per Capita for United States
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.gdpc(
    start_year: int = 2010,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    start_year : int, optional
        Start year for plot, by default 2010

    
* **Returns**

    pd.DataFrame
        DataFrame of GDP per Capita
    