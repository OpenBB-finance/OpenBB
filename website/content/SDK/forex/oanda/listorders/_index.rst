.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request the orders list from Oanda.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.listorders(
    order\_state: str = 'PENDING',
    order\_count: int = 0,
    accountID: str = 'REPLACE\_ME', chart: bool = False,
    ) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    order_state : *str*
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : *int*
        Limit the number of orders to retrieve
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    