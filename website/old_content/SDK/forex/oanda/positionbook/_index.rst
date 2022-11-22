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
forex.oanda.positionbook(
    instrument: Optional[str] = None,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

.. raw:: html

    <p>
    Request position book data for plotting.
    </p>

* **Parameters**

    instrument : Union[str, None]
        The loaded currency pair, by default None
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: bool
       Flag to display chart


* **Returns**

    Union[pd.DataFrame, bool]
        Position book data or False

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.oanda.positionbook(
    accountID: str,
    instrument: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot a position book for an instrument if Oanda provides one.
    </p>

* **Parameters**

    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

