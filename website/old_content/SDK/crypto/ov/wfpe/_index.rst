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
crypto.ov.wfpe(
    symbol: str,
    chart: bool = False,
) -> List[Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Scrapes coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]
    </p>

* **Parameters**

    symbol: str
        Coin to check withdrawal fees. By default bitcoin
    chart: bool
       Flag to display chart


* **Returns**

    List:
        - str:              Overall statistics (exchanges, lowest, average and median)
        - pandas.DataFrame: Exchange, Withdrawal Fee, Minimum Withdrawal Amount

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.wfpe(
    symbol: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]
    </p>

* **Parameters**

    symbol: str
        Coin to check withdrawal fees
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

