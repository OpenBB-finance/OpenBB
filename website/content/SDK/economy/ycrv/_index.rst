.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get yield curve for specified country. [Source: Investing.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.ycrv(
    country: str = 'United States',
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country: *str*
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().

    
* **Returns**

    pd.DataFrame
        Country yield curve
    