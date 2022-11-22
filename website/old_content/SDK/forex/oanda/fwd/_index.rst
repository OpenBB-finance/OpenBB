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
forex.oanda.fwd(
    to_symbol: str = 'USD',
    from_symbol: str = 'EUR',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Gets forward rates from fxempire
    </p>

* **Parameters**

    to_symbol: str
        To currency
    from_symbol: str
        From currency
    chart: bool
       Flag to display chart


* **Returns**

    df: pd.DataFrame

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.fwd(
    to_symbol: str = 'USD',
    from_symbol: str = 'EUR',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display forward rates for currency pairs
    </p>

* **Parameters**

    to_symbol: str
        To currency
    from_symbol: str
        From currency
    export: str
        Format to export data
    chart: bool
       Flag to display chart

