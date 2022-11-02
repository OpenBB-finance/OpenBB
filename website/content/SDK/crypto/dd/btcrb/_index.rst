.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get bitcoin price data
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.btcrb(
    start_date: str = '2010-01-01',
    end_date: str = '2022-11-02',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    start_date : *str*
        Initial date, format YYYY-MM-DD
    end_date : *str*
        Final date, format YYYY-MM-DD
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot
