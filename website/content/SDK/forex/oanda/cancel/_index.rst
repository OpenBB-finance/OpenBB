.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forex.oanda.cancel(
    orderID: str,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[str, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request cancellation of a pending order.
    </p>

* **Parameters**

    orderID : str
        The pending order ID to cancel.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.cancel(
    accountID: str,
    orderID: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Cancel a Pending Order.
    </p>

* **Parameters**

    accountID : str
        Oanda user account ID
    orderID : str
        The pending order ID to cancel.
    chart: bool
       Flag to display chart

