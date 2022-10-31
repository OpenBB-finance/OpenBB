.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns ARK orders in a Dataframe
    </h3>

{{< highlight python >}}
stocks.disc.arkord(
    buys\_only: bool = False,
    sells\_only: bool = False,
    fund: str = '',
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    buys_only: *bool*
        Flag to filter on buys only
    sells_only: *bool*
        Flag to sort on sells only
    fund: *str*
        Optional filter by fund

    
* **Returns**

    DataFrame
        ARK orders data frame with the following columns:
        ticker, date, shares, weight, fund, direction
    