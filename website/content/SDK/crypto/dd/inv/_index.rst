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
crypto.dd.inv(
    symbol: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Returns coin investors
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check investors
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        individuals
    pd.DataFrame
        organizations

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.inv(
    symbol: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display coin investors
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check coin investors
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

