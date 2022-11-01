.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Screen options based on preset filters
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.screen.screener_output(
    preset: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    preset: *str*
        Chosen preset
    
* **Returns**

    pd.DataFrame:
        DataFrame with screener data, or empty if errors
    str:
        String containing error message if supplied
    