.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request price for a forex pair.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
forex.oanda.price(
    accountID: str = 'REPLACE_ME',
    instrument: Optional[str] = None,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Union[Dict[str, str], bool]
{{< /highlight >}}

* **Parameters**

    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    instrument : Union[str, None]
        The loaded currency pair, by default None
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Union[Dict[str, str], bool]
        The currency pair price or False
