.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Historic prices for a specific option [chartexchange]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.options.hist_ce(
    symbol: str = 'GME',
    date: str = '2021-02-05',
    call: bool = True,
    price: str = '90',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol to get historical data from
    date : *str*
        Date as a string YYYYMMDD
    call : *bool*
        Whether to show a call or a put
    price : *str*
        Strike price for a specific option
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    historical : *pd.Dataframe*
        Historic information for an option
