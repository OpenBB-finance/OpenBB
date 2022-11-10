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
crypto.defi.stvl() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]
    </p>

* **Returns**

    pd.DataFrame
        Historical values of total sum of Total Value Locked from all listed protocols.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.stvl(
    limit: int = 5,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]
    </p>

* **Parameters**

    limit: int
        Number of records to display, by default 5
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

