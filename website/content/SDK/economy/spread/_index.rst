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
economy.spread(
    countries: Union[str, List[str]] = 'G7',
    maturity: str = '10Y',
    change: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get spread matrix. [Source: Investing.com]
    </p>

* **Parameters**

    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: *str*
        Maturity to get data. By default 10Y.
    change: *bool*
        Flag to use 1 day change or not. By default False.
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Spread matrix.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.spread(
    countries: Union[str, List[str]] = 'G7',
    maturity: str = '10Y',
    change: bool = False,
    color: str = 'openbb',
    raw: bool = False,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display spread matrix. [Source: Investing.com]
    </p>

* **Parameters**

    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: *str*
        Maturity to get data. By default 10Y.
    change: *bool*
        Flag to use 1 day change or not. By default False.
    color: *str*
        Color theme to use on heatmap, from rgb, binary or openbb By default, openbb.
    raw : *bool*
        Output only raw data.
    export : *str*
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: *bool*
       Flag to display chart

