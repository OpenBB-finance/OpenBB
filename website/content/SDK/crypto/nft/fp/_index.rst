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
crypto.nft.fp(
    slug, chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get nft collections [Source: https://nftpricefloor.com/]
    </p>

* **Parameters**

    slug: str
        nft collection slug
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
crypto.nft.fp(
    slug: str,
    limit: int = 10,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    raw: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]
    </p>

* **Parameters**

    slug: str
        NFT collection slug
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

