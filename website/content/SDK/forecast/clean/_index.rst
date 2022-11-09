.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.clean(
    dataset: pandas.core.frame.DataFrame,
    fill: Optional[str] = None,
    drop: Optional[str] = None,
    limit: Optional[int] = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Clean up NaNs from the dataset
    </p>

* **Parameters**

    dataset : pd.DataFrame
        The dataset you wish to clean
    fill : Optional[str]
        The method of filling NaNs
    drop : Optional[str]
        The method of dropping NaNs
    limit : Optional[int]
        The maximum limit you wish to apply that can be forward or backward filled

* **Returns**

    pd.DataFrame:
        Dataframe with cleaned up data
