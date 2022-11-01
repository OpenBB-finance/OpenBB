.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get unusual option activity from fdscanner.com
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.unu(
    limit: int = 100,
    chart: bool = False
)
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number to show

    
* **Returns**

    df: *pd.DataFrame*
        Dataframe containing options information
    last_updated: *pd.Timestamp*
        Timestamp indicated when data was updated from website
    