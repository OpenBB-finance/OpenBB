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
forex.oanda.close(
    orderID: str,
    units: Optional[int] = 0,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Close a trade.
    </p>

* **Parameters**

    orderID : str
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: bool
       Flag to display chart


* **Returns**

    Union[pd.DataFrame, bool]
        Close trades data or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.close(
    accountID: str,
    orderID: str = '',
    units: Optional[int] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Close a trade.
    </p>

* **Parameters**

    accountID : str
        Oanda user account ID
    orderID : str
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
    chart: bool
       Flag to display chart

