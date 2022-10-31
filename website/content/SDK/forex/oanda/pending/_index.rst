.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request information on pending orders.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.pending(
    accountID: str = 'REPLACE\_ME', chart: bool = False,
    ) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    
* **Returns**

    Union[pd.DataFrame, bool]
        Pending orders data or False
    