.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns a DataFrame with upcoming earnings
    </h3>

{{< highlight python >}}
stocks.disc.upcoming(
    limit: int = 10,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit : *int*
        Number of pages

* **Returns**

    DataFrame
        Upcoming earnings DataFrame
