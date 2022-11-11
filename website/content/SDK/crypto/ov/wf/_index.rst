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
crypto.ov.wf(
    limit: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Scrapes top coins withdrawal fees
    [Source: https://withdrawalfees.com/]
    </p>

* **Parameters**

    limit: int
        Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped.
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame:
        Coin, Lowest, Average, Median, Highest, Exchanges Compared

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.wf(
    limit: int = 15,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Top coins withdrawal fees
    [Source: https://withdrawalfees.com/]
    </p>

* **Parameters**

    limit: int
        Number of coins to search
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

