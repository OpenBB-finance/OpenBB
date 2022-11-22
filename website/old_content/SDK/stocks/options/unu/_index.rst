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
stocks.options.unu(
    limit: int = 100,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get unusual option activity from fdscanner.com
    </p>

* **Parameters**

    limit: int
        Number to show
    chart: bool
       Flag to display chart


* **Returns**

    df: pd.DataFrame
        Dataframe containing options information
    last_updated: pd.Timestamp
        Timestamp indicated when data was updated from website

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.unu(
    limit: int = 20,
    sortby: str = 'Vol/OI', ascend: bool = False,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays the unusual options table
    </p>

* **Parameters**

    limit: int
        Number of rows to show
    sortby: str
        Data column to sort on
    ascend: bool
        Whether to sort in ascend order
    calls_only : bool
        Flag to only show calls
    puts_only : bool
        Flag to show puts only
    export: str
        File type to export
    chart: bool
       Flag to display chart

