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
stocks.ba.messages(
    symbol: str,
    limit: int = 30,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get last messages for a given ticker [Source: stocktwits]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    limit : int
        Number of messages to get
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of messages

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.messages(
    symbol: str,
    limit: int = 30,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print up to 30 of the last messages on the board. [Source: Stocktwits]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    limit: int
        Number of messages to get
    chart: bool
       Flag to display chart

