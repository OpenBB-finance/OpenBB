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
crypto.ov.cgglobal() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get global statistics about crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    [Source: CoinGecko]
    </p>

* **Returns**

    pandas.DataFrame
        Market_Cap, Volume, Market_Cap_Percentage

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cgglobal(
    pie: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows global statistics about crypto. [Source: CoinGecko]
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct
    </p>

* **Parameters**

    pie: bool
        Whether to show a pie chart
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

