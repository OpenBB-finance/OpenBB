.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.future(
    future_type: str = 'Indices',
    sortby: str = 'ticker',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get futures data. [Source: Finviz]
    </p>

* **Parameters**

    future_type : str
        From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

* **Returns**

    pd.Dataframe
       Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
