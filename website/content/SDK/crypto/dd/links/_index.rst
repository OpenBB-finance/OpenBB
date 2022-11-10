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
crypto.dd.links(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns asset's links
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check links
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        asset links

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.links(
    symbol: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display coin links
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check links
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

