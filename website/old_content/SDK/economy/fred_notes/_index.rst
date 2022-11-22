.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.fred_notes(
    search_query: str,
    limit: int = -1,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get series notes. [Source: FRED]
    </p>

* **Parameters**

    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series notes to display

* **Returns**

    pd.DataFrame
        DataFrame of matched series
