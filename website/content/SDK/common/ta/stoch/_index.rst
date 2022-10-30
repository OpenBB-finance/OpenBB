.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Stochastic oscillator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.stoch(
    high\_vals: pandas.core.series.Series,
    low\_vals: pandas.core.series.Series,
    close\_vals: pandas.core.series.Series,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    high\_vals: *pd.Series*
        High values
    low\_vals: *pd.Series*
        Low values
    close-vals: *pd.Series*
        Close values
    fastkperiod : *int*
        Fast k period
    slowdperiod : *int*
        Slow d period
    slowkperiod : *int*
        Slow k period
    
* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
    