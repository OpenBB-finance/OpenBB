.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.clean(
    dataset: pandas.core.frame.DataFrame,
    fill: str = '',
    drop: str = '',
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
    fill : str
        The method of filling NaNs. Choose from:
        rfill, cfill, rbfill, cbfill, rffill, cffill
    drop : str
        The method of dropping NaNs. Choose from:
        rdrop, cdrop
    limit : int
        The maximum limit you wish to apply that can be forward or backward filled

* **Returns**

    pd.DataFrame:
        Dataframe with cleaned up data
