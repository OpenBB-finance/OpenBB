.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.sto(
    dataset: pandas.core.frame.DataFrame,
    close_column: str = 'close',
    high_column: str = 'high',
    low_column: str = 'low',
    period: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing
    price of a security to a range of its prices over a certain period of time. %K and %D are slow and fast indicators.

    Requires Low/High/Close columns.
    Note: This will drop first rows equal to period due to how this metric is calculated.
    </p>

* **Parameters**

    dataset : pd.DataFrame
        The dataset you wish to calculate for
    period : int
        Span

* **Returns**

    pd.DataFrame:
        Dataframe with added STO K & D columns
