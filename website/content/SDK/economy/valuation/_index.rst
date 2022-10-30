.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get group (sectors, industry or country) valuation data. [Source: Finviz]
    </h3>

{{< highlight python >}}
economy.valuation(
    group: str = 'sector',
    sortby: str = 'Name',
    ascend: bool = True,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    group : *str*
       Group by category. Available groups can be accessed through get\_groups().
    sortby : *str*
        Column to sort by
    ascend : *bool*
        Flag to sort in ascending order

    
* **Returns**

    pd.DataFrame
        dataframe with valuation/performance data
    