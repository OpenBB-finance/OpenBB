.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request data of significant events calendar.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.calendar(
    days: int,
    instrument: Optional[str] = None,
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    instrument : Union[str, None]
        The loaded currency pair, by default None
    days : *int*
        Number of days in advance

    
* **Returns**

    Union[pd.DataFrame, bool]
        Calendar events data or False
    