.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
common.qa.sortino(
    data: pandas.core.frame.DataFrame,
    target_return: float = 0,
    window: float = 252,
    adjusted: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculates the sortino ratio
    </p>

* **Parameters**

    data: pd.DataFrame
        selected dataframe
    target_return: float
        target return of the asset
    window: float
        length of the rolling window
    adjusted: bool
        adjust the sortino ratio
    chart: bool
       Flag to display chart


* **Returns**

    sortino: pd.DataFrame
        sortino ratio

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.sortino(
    data: pandas.core.frame.DataFrame,
    target_return: float,
    window: float,
    adjusted: bool,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays the sortino ratio
    </p>

* **Parameters**

    data: pd.DataFrame
        selected dataframe
    target_return: float
        target return of the asset
    window: float
        length of the rolling window
    adjusted: bool
        adjust the sortino ratio
    chart: bool
       Flag to display chart

