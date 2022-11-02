.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculates Impermanent Loss in a custom liquidity pool
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.tools.il(
    price_changeA: float,
    price_changeB: float,
    proportion: float,
    initial_pool_value: float,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    price_changeA: *float*
        price change of crypto A in percentage
    price_changeB: *float*
        price change of crypto B in percentage
    proportion: *float*
        percentage of first token in pool
    initial_pool_value: *float*
        initial value that pool contains
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Tuple:
        - pd.DataFrame: *dataframe with results*
        - str: *narrative version of results*
