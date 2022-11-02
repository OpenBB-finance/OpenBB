.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns the total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.eb(
    symbol: str,
    exchange: str = 'binance',
    start_date: int = 1262304000,
    end_date: int = 1667398713,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Asset to search active addresses (e.g., BTC)
    exchange : *str*
        Exchange to check net position change (e.g., binance)
    start_date : *int*
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : *int*
        End date timestamp (e.g., 1_614_556_800)
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        total amount of coins in units/percentage and symbol price over time
