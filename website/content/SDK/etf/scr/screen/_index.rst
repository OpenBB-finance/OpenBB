.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),
    which is updated hourly through the market day
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
etf.scr.screen(
    preset: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    preset: *str*
        Screener to use from presets
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    df : *pd.DataFrame*
        Screened dataframe
