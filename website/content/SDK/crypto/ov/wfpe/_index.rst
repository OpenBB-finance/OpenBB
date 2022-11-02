.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrapes coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.wfpe(
    symbol: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> List[Any]
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Coin to check withdrawal fees. By default bitcoin
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    List:
        - str:              Overall statistics (exchanges, lowest, average and median)
        - pandas.DataFrame: Exchange, Withdrawal Fee, Minimum Withdrawal Amount
