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
crypto.ov.cbpairs(
    limit: int = 50,
    sortby: str = 'quote_increment',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get a list of available currency pairs for trading. [Source: Coinbase]

    base_min_size - min order size
    base_max_size - max order size
    min_market_funds -  min funds allowed in a market order.
    max_market_funds - max funds allowed in a market order.
    </p>

* **Parameters**

    limit: int
        Top n of pairs
    sortby: str
        Key to sortby data
    ascend: bool
        Sort descending flag
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Available trading pairs on Coinbase

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cbpairs(
    limit: int = 20,
    sortby: str = 'quote_increment',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays a list of available currency pairs for trading. [Source: Coinbase]
    </p>

* **Parameters**

    limit: int
        Top n of pairs
    sortby: str
        Key to sortby data
    ascend: bool
        Sort ascending flag
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

