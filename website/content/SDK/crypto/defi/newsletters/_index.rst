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
crypto.defi.newsletters() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Scrape all substack newsletters from url list.
    [Source: substack.com]
    </p>

* **Returns**

    pd.DataFrame
        DataFrame with recent news from most popular DeFi related newsletters.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.newsletters(
    limit: int = 10,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display DeFi related substack newsletters.
    [Source: substack.com]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

