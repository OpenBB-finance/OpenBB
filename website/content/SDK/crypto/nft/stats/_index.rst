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
crypto.nft.stats(
    slug: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get stats of a nft collection [Source: opensea.io]
    </p>

* **Parameters**

    slug : str
        Opensea collection slug. If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        collection stats

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.nft.stats(
    slug: str,
    export: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display collection stats. [Source: opensea.io]
    </p>

* **Parameters**

    slug: str
        Opensea collection slug.
        If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

