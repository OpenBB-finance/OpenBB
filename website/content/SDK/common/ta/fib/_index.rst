.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate Fibonacci levels
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.fib(
    data: pandas.core.frame.DataFrame,
    limit: int = 120,
    start\_date: Any = None,
    end\_date: Any = None,
    chart: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, pandas.\_libs.tslibs.timestamps.Timestamp, pandas.\_libs.tslibs.timestamps.Timestamp, float, float]
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Dataframe of prices
    limit : *int*
        Days to look back for retracement
    start\_date : *Any*
        Custom start date for retracement
    end\_date : *Any*
        Custom end date for retracement

    
* **Returns**

    df : *pd.DataFrame*
        Dataframe of fib levels
    min\_date: *pd.Timestamp*
        Date of min point
    max\_date: pd.Timestamp:
        Date of max point
    min\_pr: *float*
        Price at min point
    max\_pr: *float*
        Price at max point
    