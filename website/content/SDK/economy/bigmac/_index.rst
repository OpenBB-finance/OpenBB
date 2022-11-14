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
economy.bigmac(
    country_codes: List[str] = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Display Big Mac Index for given countries
    </p>

* **Parameters**

    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe with Big Mac indices converted to USD equivalent.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.bigmac(
    country_codes: List[str] = None,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Big Mac Index for given countries
    </p>

* **Parameters**

    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

