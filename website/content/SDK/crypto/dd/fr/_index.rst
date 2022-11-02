.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin fundraising
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.fr(
    symbol: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[str, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check fundraising
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    str
        launch summary
    pd.DataFrame
        Sales rounds
    pd.DataFrame
        Treasury Accounts
    pd.DataFrame
        Metric Value launch details
