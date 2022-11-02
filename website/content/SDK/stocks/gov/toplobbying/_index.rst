.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Corporate lobbying details
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.gov.toplobbying(
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        DataFrame of top corporate lobbying
