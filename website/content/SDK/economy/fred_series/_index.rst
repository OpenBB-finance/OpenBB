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
    series_ids: List[str],
    start_date: str = None,
    end_date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    series_ids : List[str]
        Series ID to get data from
    start_date : *str*
        Start date to get data from, format yyyy-mm-dd
    end_date : *str*
        End data to get from, format yyyy-mm-dd

    
* **Returns**

    pd.DataFrame
        Series data
    