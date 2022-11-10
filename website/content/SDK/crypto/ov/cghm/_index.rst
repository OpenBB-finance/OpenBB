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
crypto.ov.cghm(
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
crypto.ov.cghm(
    category: str = '',
    limit: int = 15,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows cryptocurrencies heatmap [Source: CoinGecko]
    </p>

* **Parameters**

    caterogy: str
        Category (e.g., stablecoins). Empty for no category (default: )
    limit: int
        Number of top cryptocurrencies to display
    export: str
        Export dataframe data to csv,json,xlsx
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

