.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request cancellation of a pending order.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
forex.oanda.cancel(
    orderID: str,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Union[str, bool]
{{< /highlight >}}

* **Parameters**

    orderID : *str*
        The pending order ID to cancel.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot
