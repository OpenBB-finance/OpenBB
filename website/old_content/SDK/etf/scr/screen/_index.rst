.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
etf.scr.screen(
    preset: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),
    which is updated hourly through the market day
    </p>

* **Parameters**

    preset: str
        Screener to use from presets
    chart: bool
       Flag to display chart


* **Returns**

    df : pd.DataFrame
        Screened dataframe

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.scr.screen(
    preset: str,
    num_to_show: int,
    sortby: str,
    ascend: bool,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display screener output
    </p>

* **Parameters**

    preset: str
        Preset to use
    num_to_show: int
        Number of etfs to show
    sortby: str
        Column to sort by
    ascend: bool
        Ascend when sorted
    export: str
        Output format of export
    chart: bool
       Flag to display chart

