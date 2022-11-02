.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Converts apr into apy
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.tools.apy(
    apr: float,
    compounding_times: int,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    apr: *float*
        value in percentage
    compounding_times: *int*
        number of compounded periods in a year

    
* **Returns**

    Tuple:
        - pd.DataFrame: *dataframe with results*
        - str: *narrative version of results*
   