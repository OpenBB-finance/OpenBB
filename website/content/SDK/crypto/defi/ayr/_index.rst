.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.defi.ayr(
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        Dataframe containing historical data
