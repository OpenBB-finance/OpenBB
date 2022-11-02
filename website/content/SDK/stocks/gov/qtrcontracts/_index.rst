.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Analyzes quarterly contracts by ticker
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.gov.qtrcontracts(
    analysis: str = 'total',
    limit: int = 5,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    analysis : *str*
        How to analyze.  Either gives total amount or sorts by high/low momentum.
    limit : int, optional
        Number to return, by default 5
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe with tickers and total amount if total selected.
