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
crypto.ov.cghold(
    endpoint: str = 'bitcoin',
    chart: bool = False,
) -> List[Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]
    </p>

* **Parameters**

    endpoint : str
        "bitcoin" or "ethereum"
    chart: bool
       Flag to display chart


* **Returns**

    List:
        - str:              Overall statistics
        - pandas.DataFrame: Companies holding crypto

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cghold(
    symbol: str,
    show_bar: bool = False,
    export: str = '',
    limit: int = 15,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]
    </p>

* **Parameters**

    symbol: str
        Cryptocurrency: ethereum or bitcoin
    show_bar : bool
        Whether to show a bar graph for the data
    export: str
        Export dataframe data to csv,json,xlsx
    limit: int
        The number of rows to show
    chart: bool
       Flag to display chart

