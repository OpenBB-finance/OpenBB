.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.arkord(
    buys_only: bool = False,
    sells_only: bool = False,
    fund: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns ARK orders in a Dataframe
    </p>

* **Parameters**

    buys_only: bool
        Flag to filter on buys only
    sells_only: bool
        Flag to sort on sells only
    fund: str
        Optional filter by fund

* **Returns**

    DataFrame
        ARK orders data frame with the following columns:
        ticker, date, shares, weight, fund, direction
