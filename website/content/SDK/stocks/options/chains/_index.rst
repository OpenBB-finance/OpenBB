.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Display option chains [Source: Tradier]"
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.options.chains(
    symbol: str,
    expiry: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker to get options for
    expiry : *str*
        Expiration date in the form of "YYYY-MM-DD"
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    chains: *pd.DataFrame*
        Dataframe with options for the given Symbol and Expiration date
