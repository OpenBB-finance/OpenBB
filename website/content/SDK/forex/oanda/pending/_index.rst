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
forex.oanda.pending(
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request information on pending orders.
    </p>

* **Parameters**

    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: bool
       Flag to display chart


* **Returns**

    Union[pd.DataFrame, bool]
        Pending orders data or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.pending(
    accountID: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get information about pending orders.
    </p>

* **Parameters**

    accountID : str
        Oanda user account ID
    chart: bool
       Flag to display chart

