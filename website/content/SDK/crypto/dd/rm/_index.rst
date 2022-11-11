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
crypto.dd.rm(
    symbol: str,
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns coin roadmap
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check roadmap
    ascend: bool
        reverse order
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        roadmap

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.rm(
    symbol: str,
    ascend: bool = True,
    limit: int = 5,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display coin roadmap
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check roadmap
    ascend: bool
        reverse order
    limit : int
        number to show
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

