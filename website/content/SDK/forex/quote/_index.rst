.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get current exchange rate quote from alpha vantage.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
forex.quote(
    to_symbol: str = 'USD',
    from_symbol: str = 'EUR',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Dict
{{< /highlight >}}

* **Parameters**

    to_symbol : *str*
        To forex symbol
    from_symbol : *str*
        From forex symbol
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Dict
        Dictionary of exchange rate
