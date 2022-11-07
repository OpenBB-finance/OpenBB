.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.ema(
    dataset: pandas.core.frame.DataFrame,
    target_column: str = 'close',
    period: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    A moving average provides an indication of the trend of the price movement
    by cut down the amount of "noise" on a price chart.
    </p>

* **Parameters**

    dataset : pd.DataFrame
        The dataset you wish to clean
    target_column : str
        The column you wish to add the EMA to
    period : int
        Time Span

* **Returns**

    pd.DataFrame:
        Dataframe with added EMA column
