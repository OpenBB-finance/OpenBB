.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Moving average convergence divergence
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.macd(
    values: pandas.core.frame.DataFrame,
    n\_fast: int = 12,
    n\_slow: int = 26,
    n\_signal: int = 9,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    values: *pd.Series*
        Values for calculation
    n\_fast : *int*
        Fast period
    n\_slow : *int*
        Slow period
    n\_signal : *int*
        Signal period
    
* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
    