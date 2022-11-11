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
alt.oss.history(
    repo: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get repository star history
    </p>

* **Parameters**

    repo : str
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame - Columns: Date, Stars

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
alt.oss.history(
    repo: str,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display repo summary [Source: https://api.github.com]
    </p>

* **Parameters**

    repo : str
            Repository to display star history. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
            Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
            External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

