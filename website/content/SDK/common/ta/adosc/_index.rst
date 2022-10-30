.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate AD oscillator technical indicator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.adosc(
    data: pandas.core.frame.DataFrame,
    use_open: bool = False,
    fast: int = 3,
    slow: int = 10,
    chart = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Dataframe of OHLC prices
    use_open : *bool*
        Whether to use open prices
    fast: *int*
        Fast value
    slow: *int*
        Slow value

    
* **Returns**

    pd.DataFrame
        Dataframe with technical indicator
    