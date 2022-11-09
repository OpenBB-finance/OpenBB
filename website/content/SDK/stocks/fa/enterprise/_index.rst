.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.enterprise(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Financial Modeling Prep ticker enterprise
    </p>

* **Parameters**

    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data

* **Returns**

    pd.DataFrame:
        Dataframe of enterprise information
