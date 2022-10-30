.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get global statistics about crypto markets from CoinGecko API like:
        Market\_Cap, Volume, Market\_Cap\_Percentage

    [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cgglobal(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Market\_Cap, Volume, Market\_Cap\_Percentage
    