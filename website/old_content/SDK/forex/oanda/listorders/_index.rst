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
forex.oanda.listorders(
    order_state: str = 'PENDING',
    order_count: int = 0,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request the orders list from Oanda.
    </p>

* **Parameters**

    order_state : str
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : int
        Limit the number of orders to retrieve
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
forex.oanda.listorders(
    accountID: str,
    order_state: str = 'PENDING',
    order_count: int = 0,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    List order history.
    </p>

* **Parameters**

    accountID : str
        Oanda user account ID
    order_state : str
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : int
        Limit the number of orders to retrieve
    chart: bool
       Flag to display chart

