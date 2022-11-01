.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request information on open positions.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.openpositions(
    accountID: str = 'REPLACE_ME',
    chart: bool = False
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    