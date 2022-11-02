.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Search investpy for matching funds
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
funds.search(
    by: str = 'name',
    value: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    by : *str*
        Field to match on.  Can be name, issuer, isin or symbol
    value : *str*
        String that will be searched for
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe containing matches
