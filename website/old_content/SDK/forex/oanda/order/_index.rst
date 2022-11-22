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
forex.oanda.order(
    price: int = 0,
    units: int = 0,
    instrument: Optional[str] = None,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request creation of buy/sell trade order.
    </p>

* **Parameters**

    instrument : Union[str, None]
        The loaded currency pair, by default None
    price : int
        The price to set for the limit order.
    units : int
        The number of units to place in the order request.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: bool
       Flag to display chart


* **Returns**

    Union[pd.DataFrame, bool]
        Orders data or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.order(
    accountID: str,
    instrument: str = '',
    price: int = 0,
    units: int = 0,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Create a buy/sell order.
    </p>

* **Parameters**

    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    price : int
        The price to set for the limit order.
    units : int
        The number of units to place in the order request.
    chart: bool
       Flag to display chart

