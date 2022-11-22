.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.performance(
    group: str = 'sector',
    sortby: str = 'Name',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get group (sectors, industry or country) performance data. [Source: Finviz]
    </p>

* **Parameters**

    group : str
       Group by category. Available groups can be accessed through get_groups().
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

* **Returns**

    pd.DataFrame
        dataframe with performance data
