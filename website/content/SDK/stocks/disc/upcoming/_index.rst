.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.upcoming(
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns a DataFrame with upcoming earnings
    </p>

* **Parameters**

    limit : int
        Number of pages

* **Returns**

    DataFrame
        Upcoming earnings DataFrame
