.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get Series IDs. [Source: FRED]
    </h3>

{{< highlight python >}}
economy.fred_ids(
    search\_query: str,
    limit: int = -1, ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    search\_query : *str*
        Text query to search on fred series notes database
    limit : *int*
        Maximum number of series IDs to output
    
* **Returns**

    pd.Dataframe
        Dataframe with series IDs and titles
    