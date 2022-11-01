.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrapes top coins withdrawal fees
    [Source: https://withdrawalfees.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.wf(
    limit: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped.
    
* **Returns**

    pandas.DataFrame:
        Coin, Lowest, Average, Median, Highest, Exchanges Compared
    