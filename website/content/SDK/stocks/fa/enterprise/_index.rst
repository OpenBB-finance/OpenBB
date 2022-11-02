.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Financial Modeling Prep ticker enterprise
    </h3>

{{< highlight python >}}
stocks.fa.enterprise(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Fundamental analysis ticker symbol
    limit: *int*
        Number to get
    quarterly: *bool*
        Flag to get quarterly data

* **Returns**

    pd.DataFrame:
        Dataframe of enterprise information
