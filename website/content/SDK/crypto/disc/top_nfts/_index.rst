.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get top nft collections [Source: https://dappradar.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.disc.top_nfts(
    sortby: str = '',
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby: *str*
        Key by which to sort data

    
* **Returns**

    pd.DataFrame
        NFTs Columns: Name, Protocols, Floor Price [$], Avg Price [$], Market Cap [$], Volume [$]
   