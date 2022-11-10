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
crypto.disc.top_dexes(
    sortby: str = '',
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get top dexes by daily volume and users [Source: https://dappradar.com/]
    </p>

* **Parameters**

    sortby: str
        Key by which to sort data
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Top decentralized exchanges. Columns: Name, Daily Users, Daily Volume [$]

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.disc.top_dexes(
    limit: int = 10,
    export: str = '',
    sortby: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays top decentralized exchanges [Source: https://dappradar.com/]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

