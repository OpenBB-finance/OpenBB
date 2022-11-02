.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Converts apr into apy
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.tools.apy(
    apr: float,
    compounding_times: int,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    apr: *float*
        value in percentage
    compounding_times: *int*
        number of compounded periods in a year
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Tuple:
        - pd.DataFrame: *dataframe with results*
        - str: *narrative version of results*
