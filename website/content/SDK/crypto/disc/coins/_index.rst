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
crypto.disc.coins(
    limit: int = 250,
    category: str = '',
    sortby: str = 'Symbol',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get N coins from CoinGecko [Source: CoinGecko]
    </p>

* **Parameters**

    limit: int
        Number of top coins to grab from CoinGecko
    category: str
        Category of the coins we want to retrieve
    sortby: str
        Key to sort data
    ascend: bool
        Sort data in ascending order
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        N coins

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.disc.coins(
    category: str,
    limit: int = 250,
    sortby: str = 'Symbol',
    export: str = '',
    ascend: bool = False,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display top coins [Source: CoinGecko]
    </p>

* **Parameters**

    category: str
        If no category is passed it will search for all coins. (E.g., smart-contract-platform)
    limit: int
        Number of records to display
    sortby: str
        Key to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    ascend: bool
        Sort data in ascending order
    chart: bool
       Flag to display chart

