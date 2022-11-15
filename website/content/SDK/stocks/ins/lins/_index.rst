.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ins.lins(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get last insider activity for a given stock ticker. [Source: Finviz]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

    pd.DataFrame
        Latest insider trading activity
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ins.lins(
    symbol: str,
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display insider activity for a given stock ticker. [Source: Finviz]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    limit : int
        Number of latest insider activity to display
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

