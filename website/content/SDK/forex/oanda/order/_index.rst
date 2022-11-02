.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request creation of buy/sell trade order.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.order(
    price: int = 0,
    units: int = 0,
    instrument: Optional[str] = None,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    instrument : Union[str, None]
        The loaded currency pair, by default None
    price : *int*
        The price to set for the limit order.
    units : *int*
        The number of units to place in the order request.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    
* **Returns**

    Union[pd.DataFrame, bool]
        Orders data or False
   