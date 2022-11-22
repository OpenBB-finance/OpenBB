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
forex.oanda.price(
    accountID: str = 'REPLACE_ME',
    instrument: Optional[str] = None,
    chart: bool = False,
) -> Union[Dict[str, str], bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request price for a forex pair.
    </p>

* **Parameters**

    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    instrument : Union[str, None]
        The loaded currency pair, by default None
    chart: bool
       Flag to display chart


* **Returns**

    Union[Dict[str, str], bool]
        The currency pair price or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.price(
    account: str,
    instrument: Optional[str] = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    View price for loaded currency pair.
    </p>

* **Parameters**

    accountID : str
        Oanda account ID
    instrument : Union[str, None]
        Instrument code or None
    chart: bool
       Flag to display chart

