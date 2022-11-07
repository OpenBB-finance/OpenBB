.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.mom(
    dataset: pandas.core.frame.DataFrame,
    target_column: str = 'close',
    period: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    A momentum oscillator, which measures the percentage change between the current
    value and the n period past value.
    </p>

* **Parameters**

    dataset : pd.DataFrame
        The dataset you wish to calculate with
    target_column : str
        The column you wish to add the MOM to
    period : int
        Time Span

* **Returns**

    pd.DataFrame:
        Dataframe with added MOM column
