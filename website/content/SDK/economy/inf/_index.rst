.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical Inflation for United States from AlphaVantage
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.inf(
    start_year: int = 2010,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    start_year : int, optional
        Start year for plot, by default 2010

    
* **Returns**

    pd.DataFrame
        DataFrame of inflation rates
    