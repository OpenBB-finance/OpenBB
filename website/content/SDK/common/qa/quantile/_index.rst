.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Overlay Median & Quantile
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.quantile(data: pandas.core.frame.DataFrame, window: int = 14, quantile_pct: float = 0.5, chart = False) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of targeted data
    window : *int*
        Length of window
    quantile_pct: *float*
        Quantile to display

    
* **Returns**

    df_med : *pd.DataFrame*
        Dataframe of median prices over window
    df_quantile : *pd.DataFrame*
        Dataframe of gievn quantile prices over window
    