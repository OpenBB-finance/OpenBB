.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Close a trade.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.close(
    orderID: str,
    units: Optional[int] = 0,
    accountID: str = 'REPLACE\_ME', chart: bool = False,
    ) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    orderID : *str*
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    
* **Returns**

    Union[pd.DataFrame, bool]
        Close trades data or False
    