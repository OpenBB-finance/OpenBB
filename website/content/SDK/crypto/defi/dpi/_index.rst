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
crypto.defi.dpi(
    sortby: str = 'TVL_$', ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Returns
    -------
    pd.DataFrame
        List of DeFi Pulse protocols.
    </p>

* **Returns**

    pd.DataFrame
        List of DeFi Pulse protocols.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.dpi(
    limit: int = 10,
    sortby: str = 'TVL_$', ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]
    </p>

* **Parameters**

    limit: *int*
        Number of records to display
    sortby: *str*
        Key by which to sort data (Possible values are: "Rank", "Name", "Chain", "Sector",
        "30D_Users", "TVL_$", "1_Day_%"), by default TVL
    ascend: *bool*
        Flag to sort data ascending, by default False
    export : *str*
        Export dataframe data to csv,json,xlsx file, by default False
    chart: *bool*
       Flag to display chart

