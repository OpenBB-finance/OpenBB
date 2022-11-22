.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.search_index(
    keyword: list,
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Search indices by keyword. [Source: FinanceDatabase]
    </p>

* **Parameters**

    keyword: list
        The keyword you wish to search for. This can include spaces.
    limit: int
        The amount of views you want to show, by default this is set to 10.

* **Returns**

    pd.Dataframe
        Dataframe with the available options.
