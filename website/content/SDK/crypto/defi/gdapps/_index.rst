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
crypto.defi.gdapps(
    limit: int = 50,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]
    </p>

* **Parameters**

    limit: int
        Number of top dApps to display
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Information about DeFi protocols grouped by chain

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.gdapps(
    limit: int = 50,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]
    </p>

* **Parameters**

    num: int
        Number of top dApps to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

