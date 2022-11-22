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
crypto.ov.crypto_hacks(
    sortby: str = 'Platform',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get major crypto-related hacks
    [Source: https://rekt.news]
    </p>

* **Parameters**

    sortby: str
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame:
        Hacks with columns {Platform,Date,Amount [$],Audited,Slug,URL}

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.crypto_hacks(
    limit: int = 15,
    sortby: str = 'Platform',
    ascend: bool = False,
    slug: str = 'polyntwork-rekt',
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display list of major crypto-related hacks. If slug is passed
    individual crypto hack is displayed instead of list of crypto hacks
    [Source: https://rekt.news]
    </p>

* **Parameters**

    slug: str
        Crypto hack slug to check (e.g., polynetwork-rekt)
    limit: int
        Number of hacks to search
    sortby: str
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

