.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical futures [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
futures.historical(
    tickers: List[str],
    expiry: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Dict
{{< /highlight >}}

* **Parameters**

    tickers: List[str]
        List of future timeseries tickers to display
    expiry: *str*
        Future expiry date with format YYYY-MM
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Dict
        Dictionary with sector weightings allocation
