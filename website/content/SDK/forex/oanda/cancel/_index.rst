.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request cancellation of a pending order.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.cancel(
    orderID: str,
    accountID: str = 'REPLACE\_ME', chart: bool = False,
    ) -> Union[str, bool]
{{< /highlight >}}

* **Parameters**

    orderID : *str*
        The pending order ID to cancel.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    