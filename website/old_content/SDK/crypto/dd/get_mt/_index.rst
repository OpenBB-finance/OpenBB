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
crypto.dd.get_mt(
    only_free: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns available messari timeseries
    [Source: https://messari.io/]
    </p>

* **Parameters**

    only_free : bool
        Display only timeseries available for free
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        available timeseries

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.get_mt(
    limit: int = 10,
    query: str = '',
    only_free: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display messari timeseries list
    [Source: https://messari.io/]
    </p>

* **Parameters**

    limit : int
        number to show
    query : str
        Query to search across all messari timeseries
    only_free : bool
        Display only timeseries available for free
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

