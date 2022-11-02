.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get spread matrix. [Source: Investing.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
economy.spread(
    countries: Union[str, List[str]] = 'G7',
    maturity: str = '10Y',
    change: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: *str*
        Maturity to get data. By default 10Y.
    change: *bool*
        Flag to use 1 day change or not. By default False.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Spread matrix.
