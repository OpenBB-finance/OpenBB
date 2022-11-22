.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.fred_ids(
    search_query: str,
    limit: int = -1,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get Series IDs. [Source: FRED]
    </p>

* **Parameters**

    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series IDs to output

* **Returns**

    pd.Dataframe
        Dataframe with series IDs and titles
