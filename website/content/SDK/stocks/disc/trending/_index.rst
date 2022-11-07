.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.trending(
    limit: int = 5,
    chart: bool = False,
) -> list
{{< /highlight >}}

.. raw:: html

    <p>
    Returns a list of trending articles
    </p>

* **Parameters**

    limit: int
        Number of articles

* **Returns**

    list
        Trending articles list
