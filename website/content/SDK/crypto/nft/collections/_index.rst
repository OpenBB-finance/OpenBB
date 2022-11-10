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
crypto.nft.collections() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        nft collections

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.nft.collections(
    show_fp: bool = False,
    show_sales: bool = False,
    limit: int = 5,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display NFT collections. [Source: https://nftpricefloor.com/]
    </p>

* **Parameters**

    show_fp : bool
        Show NFT Price Floor for top collections
    limit: int
        Number of NFT collections to display
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

