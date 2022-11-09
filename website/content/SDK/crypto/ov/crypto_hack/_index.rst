.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.ov.crypto_hack(
    slug: str,
    chart: bool = False,
) -> Optional[str]
{{< /highlight >}}

.. raw:: html

    <p>
    Get crypto hack
    [Source: https://rekt.news]
    </p>

* **Parameters**

    slug: str
        slug of crypto hack

* **Returns**

    pandas.DataFrame:
        Hacks with columns {Platform,Date,Amount [$],Audited,URL}
