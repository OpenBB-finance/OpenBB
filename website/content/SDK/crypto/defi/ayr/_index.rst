.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.ayr(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        Dataframe containing historical data
   