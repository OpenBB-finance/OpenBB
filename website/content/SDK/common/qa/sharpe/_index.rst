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
common.qa.sharpe(
    data: pandas.core.frame.DataFrame,
    rfr: float = 0,
    window: float = 252,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculates the sharpe ratio
    </p>

* **Parameters**

    data: pd.DataFrame
        selected dataframe column
    rfr: float
        risk free rate
    window: float
        length of the rolling window
    chart: bool
       Flag to display chart


* **Returns**

    sharpe: pd.DataFrame
        sharpe ratio

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.sharpe(
    data: pandas.core.frame.DataFrame,
    rfr: float = 0,
    window: float = 252,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Calculates the sharpe ratio
    </p>

* **Parameters**

    data: pd.DataFrame
        selected dataframe column
    rfr: float
        risk free rate
    window: float
        length of the rolling window
    chart: bool
       Flag to display chart

