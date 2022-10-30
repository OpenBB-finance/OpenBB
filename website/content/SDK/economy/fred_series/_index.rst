.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get Series data. [Source: FRED]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.fred_series(
    series\_ids: List[str],
    start\_date: str = None,
    end\_date: str = None,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    series\_ids : List[str]
        Series ID to get data from
    start\_date : *str*
        Start date to get data from, format yyyy-mm-dd
    end\_date : *str*
        End data to get from, format yyyy-mm-dd

    
* **Returns**

    pd.DataFrame
        Series data
    