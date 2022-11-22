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
forex.oanda.calendar(
    days: int = 14,
    instrument: Optional[str] = None,
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request data of significant events calendar.
    </p>

* **Parameters**

    instrument : Union[str, None]
        The loaded currency pair, by default None
    days : int
        Number of days in advance
    chart: bool
       Flag to display chart


* **Returns**

    Union[pd.DataFrame, bool]
        Calendar events data or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.calendar(
    instrument: str,
    days: int = 7,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    View calendar of significant events.
    </p>

* **Parameters**

    instrument : str
        The loaded currency pair
    days : int
        Number of days in advance
    chart: bool
       Flag to display chart

