.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Display Big Mac Index for given countries
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
economy.bigmac(
    country_codes: List[str] = None,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe with Big Mac indices converted to USD equivalent.
