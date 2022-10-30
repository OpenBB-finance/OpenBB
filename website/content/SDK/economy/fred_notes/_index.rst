.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get series notes. [Source: FRED]
    </h3>

{{< highlight python >}}
economy.fred_notes(
    search_query: str,
    limit: int = -1, ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    search_query : *str*
        Text query to search on fred series notes database
    limit : *int*
        Maximum number of series notes to display
    
* **Returns**

    pd.DataFrame
        DataFrame of matched series
    