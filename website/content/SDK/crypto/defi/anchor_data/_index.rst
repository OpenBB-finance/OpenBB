.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.defi.anchor_data(
    address: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[Any, Any, str]
{{< /highlight >}}

* **Parameters**

    address : *str*
        Terra address. Valid terra addresses start with 'terra'
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Tuple:
        - pandas.DataFrame: *Earnings over time in UST*
        - pandas.DataFrame: *History of transactions*
        - str: *             Overall statistics*
