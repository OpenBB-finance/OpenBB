.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),
    which is updated hourly through the market day
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.scr.screen(
    preset: str,
    chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    preset: *str*
        Screener to use from presets

    
* **Returns**

    df : *pd.DataFrame*
        Screened dataframe
    