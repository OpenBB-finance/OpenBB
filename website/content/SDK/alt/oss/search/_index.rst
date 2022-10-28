.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get repos sorted by stars or forks. Can be filtered by categories
    </h3>

{{< highlight python >}}
alt.oss.search(sortby: str = 'stars', page: int = 1, categories: str = '') -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby : *str*
            Sort repos by {stars, forks}
    categories : *str*
            Check for repo categories. If more than one separate with a comma: *e.g., finance,investment. Default: None*
    page : *int*
            Page number to get repos
    
* **Returns**

    pd.DataFrame with list of repos
    