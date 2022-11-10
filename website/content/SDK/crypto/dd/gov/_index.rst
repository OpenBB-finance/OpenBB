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
crypto.dd.gov(
    symbol: str,
    chart: bool = False,
) -> Tuple[str, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Returns coin governance
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check governance
    chart: bool
       Flag to display chart


* **Returns**

    str
        governance summary
    pd.DataFrame
        Metric Value with governance details

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.gov(
    symbol: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display coin governance
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check coin governance
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

