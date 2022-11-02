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
economy.ycrv(
    country: str = 'United States',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get yield curve for specified country. [Source: Investing.com]
    </p>

* **Parameters**

    country: *str*
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Country yield curve

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.ycrv(
    country: str = 'United States',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    raw: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display yield curve for specified country. [Source: Investing.com]
    </p>

* **Parameters**

    country: *str*
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().
    export : *str*
        Export dataframe data to csv,json,xlsx file
    chart: *bool*
       Flag to display chart

