.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request order book data for plotting.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
forex.oanda.orderbook(
    instrument: Optional[str] = None,
    accountID: str = 'REPLACE_ME',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    instrument : Union[str, None]
        The loaded currency pair, by default None
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Union[pd.DataFrame, bool]
        Order book data or False
